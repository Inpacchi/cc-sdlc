# The CI tier's per-job runner image (z-sdlc process/factory.md, Enablement step 10, The CI tier): the project's
# toolchain image (factory.json's ci block) with the GitHub Actions runner on top. host/setup.sh builds it on the
# runner host (TIER=ci) as the runner user, and ci_launcher.py starts one container of it per job: the runner
# registers with its just-in-time config (ACTIONS_RUNNER_INPUT_JITCONFIG), runs one job and exits.
# The toolchain image must be Debian or Ubuntu (apt). The runner is linux-x64 at setup.sh's RUNNER_VERSION, its
# archive checked against RUNNER_SHA256. It may update itself when GitHub asks, inside its throwaway container only.
ARG BASE
FROM ${BASE}

ARG RUNNER_VERSION
ARG RUNNER_SHA256
ARG DEBIAN_FRONTEND=noninteractive
USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# python3: the tier's isolation check runs its probe in a container of this image.
RUN test -n "$RUNNER_VERSION" && test -n "$RUNNER_SHA256" \
 && apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl python3 \
 && install -d /actions-runner \
 && cd /actions-runner \
 && curl -fsSL -o runner.tgz \
      "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" \
 && echo "${RUNNER_SHA256}  runner.tgz" | sha256sum -c - \
 && tar xzf runner.tgz \
 && rm runner.tgz \
 && ./bin/installdependencies.sh \
 && rm -rf /var/lib/apt/lists/*

# The job runs as the container's root, which rootless Docker maps to an unprivileged user on the host, so a job
# can start its own services (Postgres) and drop them to their users. The launcher adds no-new-privileges.
ENV RUNNER_ALLOW_RUNASROOT=1
WORKDIR /actions-runner
ENTRYPOINT ["./run.sh"]
