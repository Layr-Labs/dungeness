FROM python:3.12-slim-bookworm
COPY workspace/ /workspace/repo/
COPY web_client.py /usr/local/bin/web
COPY evaluate.py /usr/local/bin/evaluate
COPY run_status.py /usr/local/bin/run-status
COPY candidate_state.py /usr/local/bin/candidate-state
RUN chmod 0555 /usr/local/bin/web /usr/local/bin/evaluate /usr/local/bin/run-status /usr/local/bin/candidate-state
WORKDIR /workspace/repo
