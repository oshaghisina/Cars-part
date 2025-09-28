#!/bin/bash

# Workflow Logging Framework
# Provides consistent logging across all workflows

set -e

# Logging functions
log_info() {
    echo "ℹ️ $1"
}

log_success() {
    echo "✅ $1"
}

log_warning() {
    echo "⚠️ $1"
}

log_error() {
    echo "❌ $1"
}

log_group_start() {
    echo "::group::$1"
}

log_group_end() {
    echo "::endgroup::"
}

log_step() {
    local step_name="$1"
    local step_description="$2"
    
    log_group_start "🔧 $step_name"
    echo "$step_description"
}

log_step_end() {
    log_group_end
}

# Job status tracking
log_job_start() {
    local job_name="$1"
    local job_description="$2"
    
    echo "🚀 Starting job: $job_name"
    echo "📋 Description: $job_description"
    echo "⏰ Started at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
}

log_job_end() {
    local job_name="$1"
    local status="$2"
    
    echo "🏁 Job completed: $job_name"
    echo "📊 Status: $status"
    echo "⏰ Finished at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
}

# Conditional execution logging
log_conditional_start() {
    local condition="$1"
    local description="$2"
    
    echo "🔍 Checking condition: $condition"
    echo "📋 Description: $description"
}

log_conditional_skip() {
    local reason="$1"
    
    echo "⏭️ Skipping: $reason"
}

log_conditional_run() {
    local reason="$1"
    
    echo "▶️ Running: $reason"
}

# Performance tracking
log_performance_start() {
    local operation="$1"
    echo "⏱️ Starting: $operation"
    echo "$operation" > /tmp/current_operation
    echo "$(date +%s)" > /tmp/operation_start_time
}

log_performance_end() {
    local operation="$1"
    local start_time=$(cat /tmp/operation_start_time 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local duration=$((current_time - start_time))
    
    echo "⏱️ Completed: $operation (${duration}s)"
    rm -f /tmp/current_operation /tmp/operation_start_time
}

# Error handling
log_error_with_context() {
    local error="$1"
    local context="$2"
    
    log_error "$error"
    echo "🔍 Context: $context"
    echo "📊 Job: $GITHUB_JOB"
    echo "🏃 Runner: $GITHUB_RUNNER_NAME"
    echo "📁 Workspace: $GITHUB_WORKSPACE"
}

# Artifact logging
log_artifact_upload() {
    local artifact_name="$1"
    local artifact_path="$2"
    
    echo "📦 Uploading artifact: $artifact_name"
    echo "📁 Path: $artifact_path"
}

log_artifact_download() {
    local artifact_name="$1"
    local download_path="$2"
    
    echo "📥 Downloading artifact: $artifact_name"
    echo "📁 Path: $download_path"
}

# Workflow summary
log_workflow_summary() {
    local workflow_name="$1"
    local total_jobs="$2"
    local successful_jobs="$3"
    local failed_jobs="$4"
    
    echo "📊 Workflow Summary: $workflow_name"
    echo "📈 Total Jobs: $total_jobs"
    echo "✅ Successful: $successful_jobs"
    echo "❌ Failed: $failed_jobs"
    echo "📊 Success Rate: $(( (successful_jobs * 100) / total_jobs ))%"
}

# Export functions for use in workflows
export -f log_info log_success log_warning log_error
export -f log_group_start log_group_end log_step log_step_end
export -f log_job_start log_job_end
export -f log_conditional_start log_conditional_skip log_conditional_run
export -f log_performance_start log_performance_end
export -f log_error_with_context
export -f log_artifact_upload log_artifact_download
export -f log_workflow_summary
