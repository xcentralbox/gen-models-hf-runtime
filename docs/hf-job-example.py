"""REFERENCE ONLY: not executed by CI. Real adapter handles private bucket mounts and admission.

Uses already-built, publicly pullable, digest-pinned GHCR image.
A list of HF model repo mounts must be built from the private pinned manifest.
"""
from huggingface_hub import HfApi, Volume

def run_example(image_digest: str, private_model_volumes: list[Volume], namespace: str, gpu: str):
    if not image_digest.startswith('ghcr.io/xcentralbox/') or '@sha256:' not in image_digest:
        raise ValueError('Immutable GHCR image digest required')
    # Do not call this method without an operator-approved budget and per-job hard timeout.
    return HfApi().run_job(
        image=image_digest,
        command=['python', '/hf/bridge/runtime/runner.py', '--job-id', 'REPLACE_WITH_VALID_JOB_ID'],
        namespace=namespace,
        flavor=gpu,
        timeout=300,
        volumes=private_model_volumes,
    )
