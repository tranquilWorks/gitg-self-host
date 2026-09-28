#!/usr/bin/env bash
set -Eeuo pipefail

readonly repo_root="/home/kbianco/gitg-self-host"
cd "$repo_root"

for required_command in docker curl python3; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        printf 'Required command is unavailable: %s\n' "$required_command" >&2
        exit 1
    fi
done
docker compose version

readonly probe_dir="/tmp/grounded-growth-compose-smoke.7WZF2i"
readonly initial_env="$probe_dir/initial.env"
readonly changed_env="$probe_dir/changed.env"
readonly project_name="ggsmokelocal01279499"
readonly username="compose-probe"
readonly original_password="Original-probe-password-47!"
readonly persisted_password="Persisted-probe-password-58!"
readonly changed_env_password="Changed-env-password-69!"
readonly backup_path="/data/backups/compose-smoke.sqlite3"
readonly expected_counts="37,383,1403,383,383,383,37"

SMOKE_APP_PORT=45545
if [[ -n "${SMOKE_APP_PORT:-}" ]]; then
    readonly app_port="$SMOKE_APP_PORT"
else
    readonly app_port="$(
        python3 -c \
            'import socket; sock = socket.socket(); sock.bind(("127.0.0.1", 0)); print(sock.getsockname()[1]); sock.close()'
    )"
fi
readonly base_url="http://127.0.0.1:$app_port"

write_env() {
    local path="$1"
    local password="$2"
    {
        printf 'APP_PORT=%s\n' "$app_port"
        printf 'DJANGO_SECRET_KEY=compose-smoke-only-secret-key-with-sufficient-length-47\n'
        printf 'DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\n'
        printf 'APP_BOOTSTRAP_USERNAME=%s\n' "$username"
        printf 'APP_BOOTSTRAP_PASSWORD=%s\n' "$password"
        printf 'APP_TIME_ZONE=UTC\n'
        printf 'APP_DEBUG=false\n'
        printf 'APP_SECURE_COOKIES=false\n'
        printf 'APP_OWNER_RETENTION_ENABLED=false\n'
        printf 'APP_OWNER_RETENTION_DAYS=365\n'
        printf 'GUNICORN_WORKERS=1\n'
    } >"$path"
}

active_env="$changed_env"

compose() {
    APP_ENV_FILE="$active_env" APP_PORT="$app_port" \
        docker compose --project-name "$project_name" "$@"
}

cleanup() {
    local status=$?
    trap - EXIT
    if ((status != 0)); then
        printf '\nCompose verification failed; final service state and logs follow.\n' >&2
        compose ps >&2 || true
        compose logs --no-color app >&2 || true
    fi
    if [[ "$project_name" == ggsmoke* ]]; then
        compose down --volumes --remove-orphans >/dev/null 2>&1 || true
    fi
    rm -f -- "$initial_env" "$changed_env"
    rmdir "$probe_dir" 2>/dev/null || true
    exit "$status"
}
trap cleanup EXIT

http_probe() {
    local password="$1"
    local expectation="$2"
    local boundary_option=()
    if [[ "$expectation" == "failure" ]]; then
        boundary_option=(--skip-public-boundary)
    fi
    python3 scripts/verify_http_login.py \
        --base-url "$base_url" \
        --username "$username" \
        --password "$password" \
        --expect "$expectation" \
        --authenticated-path "/personal-os/" \
        "${boundary_option[@]}"
}

canonical_counts() {
    compose exec -T app python manage.py shell -c \
        'from growth.models import Competency, CompetencyLeverLink, Lever, LeverBaseline, PracticeProtocol; print(",".join(str(value) for value in (Lever.objects.count(), Competency.objects.count(), CompetencyLeverLink.objects.count(), PracticeProtocol.objects.count(), PracticeProtocol.objects.filter(availability=PracticeProtocol.Availability.ACTIVE).count(), PracticeProtocol.objects.filter(score_active=True).count(), LeverBaseline.objects.count())))' \
        | tail -n 1
}

browser_slice_state() {
    compose exec -T app python manage.py shell -c \
        'import hashlib; from growth.models import AssessmentContext, AssessmentRun, PersonalOSRevision, PracticeContext, PracticeProtocol, WeeklyExecutionPlan, WeeklyExecutionReview; from growth.services.context_priority import build_context_priority_for_epoch; run=AssessmentRun.objects.select_related("user").order_by("stable_id").first(); personal=tuple(PersonalOSRevision.objects.order_by("assessment_run_id","revision").values_list("content_hash",flat=True)); assessment=tuple(AssessmentContext.objects.order_by("assessment_run_id","revision").values_list("content_hash",flat=True)); practice=tuple(PracticeContext.objects.order_by("assessment_run_id","protocol_id","revision").values_list("content_hash",flat=True)); weekly_plans=tuple(WeeklyExecutionPlan.objects.order_by("assessment_run_id","week_start","revision").values_list("content_hash",flat=True)); weekly_reviews=tuple(WeeklyExecutionReview.objects.order_by("plan_id").values_list("content_hash",flat=True)); priority=build_context_priority_for_epoch(user=run.user,assessment_run=run,protocol_stable_ids=("PRACTICE-FRIENDSHIP-01",)); active=tuple(PracticeProtocol.objects.filter(score_active=True).order_by("stable_id").values_list("stable_id",flat=True)); active_hash=hashlib.sha256(chr(44).join(active).encode()).hexdigest(); print("|".join((f"personal={len(personal)}:{chr(44).join(personal)}",f"assessment={len(assessment)}:{chr(44).join(assessment)}",f"practice={len(practice)}:{chr(44).join(practice)}",f"weekly_plans={len(weekly_plans)}:{chr(44).join(weekly_plans)}",f"weekly_reviews={len(weekly_reviews)}:{chr(44).join(weekly_reviews)}",f"priority={priority.content_hash}",f"score_active={len(active)}:{active_hash}")))' \
        | tail -n 1
}

printf '\n==> Resume interrupted smoke after restored container is healthy\n'
compose exec -T app python manage.py verify_database_backup "$backup_path" --compare-live
readonly expected_browser_slice_state="$(browser_slice_state)"
[[ "$expected_browser_slice_state" =~ ^personal=1:[0-9a-f]{64}\|assessment=1:[0-9a-f]{64}\|practice=1:[0-9a-f]{64}\|weekly_plans=1:[0-9a-f]{64}\|weekly_reviews=1:[0-9a-f]{64}\|priority=[0-9a-f]{64}\|score_active=383:[0-9a-f]{64}$ ]]
printf 'Restored browser state captured only after backup critical-state equality passed.\n'
compose exec -T app python manage.py migrate --check
compose exec -T app python manage.py verify_database_backup "$backup_path" --compare-live
http_probe "$original_password" success
http_probe "$persisted_password" failure
http_probe "$changed_env_password" failure
test "$(canonical_counts)" = "$expected_counts"
compose exec -T app python manage.py rebuild_score_state --verify-only
compose exec -T app python manage.py rebuild_composite_score_state --verify-only
compose exec -T app python manage.py verify_composite_scoring_readiness
compose exec -T app python manage.py verify_pilot_readiness
compose exec -T app python manage.py verify_expansion_readiness
compose exec -T app python manage.py verify_competency_evidence_readiness
compose exec -T app python manage.py verify_context_readiness
compose exec -T app python manage.py verify_personal_os_readiness
compose exec -T app python manage.py verify_context_priority_readiness
compose exec -T app python manage.py verify_m6c_pilot_readiness
compose exec -T app python manage.py verify_m6d_authoring_readiness
compose exec -T app python manage.py verify_weekly_execution_readiness
compose exec -T app python manage.py verify_m6h_operations_readiness
compose exec -T app python manage.py verify_assessment_calibration_collection
compose exec -T app python manage.py verify_assessment_calibration_analysis
test "$(browser_slice_state)" = "$expected_browser_slice_state"

printf '\n==> Confirm clean Gunicorn shutdown\n'
compose stop --timeout 30 app
test "$(docker inspect --format '{{.State.ExitCode}}' "$(compose ps -a -q app)")" = "0"

printf '\nDocker Compose deployment verification passed.\n'
