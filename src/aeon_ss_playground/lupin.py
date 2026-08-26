from copy import deepcopy

import numpy as np

import spikeinterface.full as si

from spikeinterface.core import (
    NumpySorting,
    estimate_templates_with_accumulator,
    Templates,
    ms_to_samples,
    get_noise_levels,
)

from spikeinterface.sortingcomponents.tools import create_sorting_analyzer_with_existing_templates

from spikeinterface.core.base import minimum_spike_dtype

# STEP 2
from spikeinterface.sortingcomponents.tools import (
    get_prototype_and_waveforms_from_recording,
)
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_selection import select_peaks
from spikeinterface.sortingcomponents.clustering.main import (
    find_clusters_from_peaks,
    clustering_methods,
)
from spikeinterface.sortingcomponents.tools import (
    clean_templates,
    compute_sparsity_from_peaks_and_label,
)

# STEP 3
from spikeinterface.sortingcomponents.matching import find_spikes_from_templates
from spikeinterface.sorters.internal.spyking_circus2 import final_cleaning_circus

from spikeinterface.sortingcomponents.tools import cache_preprocessing, clean_cache_preprocessing


_default_params = {
    "apply_preprocessing": True,
    "preprocessing_dict": None,
    "apply_motion_correction": True,
    "motion_correction_preset": "dredge_fast",
    "clustering_ms_before": 0.3,
    "clustering_ms_after": 1.3,
    "whitening_radius_um": 100.0,
    "detection_radius_um": 50.0,
    "features_radius_um": 120.0,
    "split_radius_um": 60.0,
    "template_radius_um": 100.0,
    "merge_similarity_lag_ms": 0.5,
    "freq_min": 150.0,
    "freq_max": 7000.0,
    "cache_preprocessing_mode": "folder",
    "peak_sign": "neg",
    "detect_threshold": 5.0,
    "n_peaks_per_channel": 5000,
    "n_svd_components_per_channel": 5,
    "n_pca_features": 4,
    "clustering_recursive_depth": 3,
    "ms_before": 1.0,
    "ms_after": 2.5,
    "template_sparsify_threshold": 1.0,
    "template_min_snr_ptp": 4.0,
    "template_max_jitter_ms": 0.2,
    "template_matching_engine": "wobble",
    "min_firing_rate": 0.1,
    "gather_mode": "memory",
    "job_kwargs": {},
    "seed": None,
    "save_array": True,
    "debug": False,
}

def preprocess_recording(recording_raw, params, seed):

    # STEP 1: preprocess the recording
    recording = si.bandpass_filter(
        recording_raw,
        freq_min=params["freq_min"],
        freq_max=params["freq_max"],
        ftype="bessel",
        filter_order=2,
        dtype="float32",
    )
    recording = si.common_reference(recording)

    recording = recording.astype("float32")

    recording = si.whiten(
        recording,
        dtype="float32",
        mode="local",
        radius_um=params["whitening_radius_um"],
        seed=seed,
    )

    return recording
    

def make_template_library(recording_raw, templates_folder):

    verbose = True

    params = _default_params

    seed = 1205

    num_chans = recording_raw.get_num_channels()
    sampling_frequency = recording_raw.get_sampling_frequency()

    recording = preprocess_recording(recording_raw, params, seed)

    noise_levels = get_noise_levels(
        recording, return_in_uV=False, random_slices_kwargs=dict(seed=seed)
    )
    # STEP 2: make templates

    job_kwargs = {}

    # detection
    ms_before = params["ms_before"]
    ms_after = params["ms_after"]
    prototype, few_waveforms, few_peaks = get_prototype_and_waveforms_from_recording(
        recording,
        n_peaks=10_000,
        ms_before=ms_before,
        ms_after=ms_after,
        seed=seed,
        noise_levels=noise_levels,
        job_kwargs=job_kwargs,
    )

    detection_params = dict(
        peak_sign=params["peak_sign"],
        detect_threshold=params["detect_threshold"],
        exclude_sweep_ms=1.5,
        radius_um=params["detection_radius_um"],
        prototype=prototype,
        ms_before=ms_before,
    )

    all_peaks = detect_peaks(
        recording,
        method="matched_filtering",
        method_kwargs=detection_params,
        job_kwargs=job_kwargs,
    )

    print(f"detect_peaks(): {len(all_peaks)} peaks found")

    # selection
    n_peaks = max(params["n_peaks_per_channel"] * num_chans, 20_000)
    peaks = select_peaks(all_peaks, method="uniform", n_peaks=n_peaks)
    print(f"select_peaks(): {len(peaks)} peaks kept for clustering")

    num_shifts_merging = int(
        sampling_frequency * params["merge_similarity_lag_ms"] / 1000.0
    )

    # Clustering
    clustering_kwargs = deepcopy(
        clustering_methods["iterative-isosplit"]._default_params
    )
    clustering_kwargs["peaks_svd"]["ms_before"] = params["clustering_ms_before"]
    clustering_kwargs["peaks_svd"]["ms_after"] = params["clustering_ms_after"]
    clustering_kwargs["peaks_svd"]["radius_um"] = params["features_radius_um"]
    clustering_kwargs["peaks_svd"]["n_components"] = params[
        "n_svd_components_per_channel"
    ]
    clustering_kwargs["split"]["split_radius_um"] = params["split_radius_um"]
    clustering_kwargs["split"]["recursive_depth"] = params["clustering_recursive_depth"]
    clustering_kwargs["split"]["method_kwargs"]["n_pca_features"] = params[
        "n_pca_features"
    ]
    clustering_kwargs["clean_templates"]["sparsify_threshold"] = params[
        "template_sparsify_threshold"
    ]
    clustering_kwargs["clean_templates"]["min_snr"] = params["template_min_snr_ptp"]
    clustering_kwargs["clean_templates"]["max_jitter_ms"] = params[
        "template_max_jitter_ms"
    ]
    clustering_kwargs["merge_from_templates"]["use_lags"] = True
    clustering_kwargs["merge_from_templates"]["num_shifts"] = num_shifts_merging
    clustering_kwargs["noise_levels"] = noise_levels
    clustering_kwargs["clean_low_firing"]["min_firing_rate"] = params["min_firing_rate"]

    clustering_kwargs["clean_low_firing"]["subsampling_factor"] = (
        all_peaks.size / peaks.size
    )
    clustering_kwargs["seed"] = seed

    clustering_kwargs["debug_folder"] = templates_folder / 'debug'

    # sam suggests playing with this
    clustering_kwargs["isocut_threshold"] = 2.0

    unit_ids, clustering_label, more_outs = find_clusters_from_peaks(
        recording,
        peaks,
        method="iterative-isosplit",
        method_kwargs=clustering_kwargs,
        extra_outputs=True,
        job_kwargs=job_kwargs,
    )

    if more_outs["time_shifts"] is not None:
        time_shifts = more_outs["time_shifts"]
        peaks["sample_index"] += time_shifts

    mask = clustering_label >= 0
    kept_peaks = peaks[mask]
    kept_labels = clustering_label[mask]

    sorting_pre_peeler = NumpySorting.from_samples_and_labels(
        kept_peaks["sample_index"],
        kept_labels,
        sampling_frequency,
        unit_ids=unit_ids,
    )
    if verbose:
        print(f"find_clusters_from_peaks(): {unit_ids.size} cluster found")

    # preestimate the sparsity using peaks channel
    spike_vector = sorting_pre_peeler.to_spike_vector(concatenated=True)
    sparsity, unit_locations = compute_sparsity_from_peaks_and_label(
        kept_peaks,
        spike_vector["unit_index"],
        sorting_pre_peeler.unit_ids,
        recording,
        params["template_radius_um"],
    )

    # Template are sparse from radius using unit_location
    nbefore = ms_to_samples(ms_before, sampling_frequency)
    nafter = ms_to_samples(ms_after, sampling_frequency)
    templates_array = estimate_templates_with_accumulator(
        recording,
        sorting_pre_peeler.to_spike_vector(),
        sorting_pre_peeler.unit_ids,
        nbefore,
        nafter,
        return_in_uV=False,
        sparsity_mask=sparsity.mask,
        **job_kwargs,
    )
    templates = Templates(
        templates_array=templates_array,
        sampling_frequency=sampling_frequency,
        nbefore=nbefore,
        channel_ids=recording.channel_ids,
        unit_ids=sorting_pre_peeler.unit_ids,
        sparsity_mask=sparsity.mask,
        probe=recording.get_probe(),
        is_in_uV=False,
    )

    # this spasify more
    templates = clean_templates(
        templates,
        sparsify_threshold=params["template_sparsify_threshold"],
        noise_levels=noise_levels,
        min_snr=params["template_min_snr_ptp"],
        max_jitter_ms=params["template_max_jitter_ms"],
        remove_empty=True,
    )

    templates.to_zarr(templates_folder)

def do_template_matching(recording_raw, templates_folder, sorter_output_folder):

    sampling_frequency = recording_raw.get_sampling_frequency()

    templates = si.load(templates_folder)

    params = _default_params
    seed = 1205

    recording = preprocess_recording(recording_raw, params, seed)
    recording, cache_info = cache_preprocessing(
        recording,
        mode=params["cache_preprocessing_mode"],
        folder=sorter_output_folder / 'cache',
    )
    noise_levels = get_noise_levels(
        recording, return_in_uV=False, random_slices_kwargs=dict(seed=seed)
    )

    # Template matching
    gather_mode = params["gather_mode"]
    pipeline_kwargs = dict(gather_mode=gather_mode)
    spikes = find_spikes_from_templates(
        recording,
        templates,
        method=params["template_matching_engine"],
        method_kwargs={},
        pipeline_kwargs=pipeline_kwargs,
        job_kwargs={},
    )

    final_spikes = np.zeros(spikes.size, dtype=minimum_spike_dtype)
    final_spikes["sample_index"] = spikes["sample_index"]
    final_spikes["unit_index"] = spikes["cluster_index"]
    final_spikes["segment_index"] = spikes["segment_index"]
    sorting = NumpySorting(final_spikes, sampling_frequency, templates.unit_ids)

    analyzer_final = create_sorting_analyzer_with_existing_templates(
        sorting, recording, templates, noise_levels=noise_levels,
    )
    analyzer_final._recording = recording
    analyzer_final.save_as(format="binary_folder", folder=sorter_output_folder / "lupin_temp_analyzer")

    clean_cache_preprocessing(cache_info)

    return analyzer_final