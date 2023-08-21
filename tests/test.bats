load 'test_helper'

### Hello World tests

@test "[hello-world] - hello_world_t.py" {
  runExample $HELLO_WORLD_DIR hello_world_t.py
  assert_success
}

### Howtos tests

@test "[howtos] - acouchbase_n1ql_ops.py" {
  runExample $HOWTOS_DIR acouchbase_n1ql_ops.py
  assert_success
}

@test "[howtos] - acouchbase_operations.py" {
  runExample $HOWTOS_DIR acouchbase_operations.py
  assert_success
}

@test "[howtos] - acouchbase_search_ops.py" {
  runExample $HOWTOS_DIR acouchbase_search_ops.py
  assert_success
}

@test "[howtos] - encrypting_using_sdk.py" {
  skip "Very, very broken"
  runExample $HOWTOS_DIR encrypting_using_sdk.py
  assert_success
}

@test "[howtos] - error_handling.py" {
  runExample $HOWTOS_DIR error_handling.py
  assert_success
}

@test "[howtos] - health_check.py" {
  runExample $HOWTOS_DIR health_check.py
  assert_success
}

@test "[howtos] - kv_operations.py" {
  runExample $HOWTOS_DIR kv_operations.py
  assert_success
}

@test "[howtos] - logging_example.py" {
  runExample $HOWTOS_DIR logging_example.py
  # Raises an error on purpose to log it
  assert_failure 134
}

@test "[howtos] - managing_connections.py" {
  runExample $HOWTOS_DIR managing_connections.py
  assert_success
}

@test "[howtos] - n1ql_ops.py" {
  runExample $HOWTOS_DIR n1ql_ops.py
  assert_success
}

@test "[howtos] - orphan_logging.py" {
  skip "Example currently broken (C++ core)"
  runExample $HOWTOS_DIR orphan_logging.py
  assert_failure
}

@test "[howtos] - provisioning_resources_buckets.py" {
  runExample $HOWTOS_DIR provisioning_resources_buckets.py
  assert_success
}

@test "[howtos] - provisioning_resources_collections.py" {
  runExample $HOWTOS_DIR provisioning_resources_collections.py
  assert_success
}

@test "[howtos] - provisioning_resources_users.py" {
  runExample $HOWTOS_DIR provisioning_resources_users.py
  assert_success
}

@test "[howtos] - provisioning_resources_views.py" {
  runExample $HOWTOS_DIR provisioning_resources_views.py
  assert_success
}

@test "[howtos] - query_index_manager.py" {
  runExample $HOWTOS_DIR query_index_manager.py
  assert_success
}

@test "[howtos] - search_ops.py" {
  runExample $HOWTOS_DIR search_ops.py
  assert_success
}

@test "[howtos] - subdocument_ops.py" {
  runExample $HOWTOS_DIR subdocument_ops.py
  assert_success
}

@test "[howtos] - threshold_logging.py" {
  runExample $HOWTOS_DIR threshold_logging.py
  assert_success
}

@test "[howtos] - transactions_example.py" {
  runExample $HOWTOS_DIR transactions_example.py
  assert_success
}

@test "[howtos] - transcoders.py" {
  runExample $HOWTOS_DIR transcoders.py
  assert_success
}

@test "[howtos] - txcouchbase_n1ql_ops.py" {
  skip "txcouchbase api has been effectively deprecated"
  runExample $HOWTOS_DIR txcouchbase_n1ql_ops.py
  assert_success
}

@test "[howtos] - txcouchbase_operations.py" {
  skip "txcouchbase api has been effectively deprecated"
  runExample $HOWTOS_DIR txcouchbase_operations.py
  assert_success
}

@test "[howtos] - txcouchbase_search_ops.py" {
  skip "txcouchbase api has been effectively deprecated"
  runExample $HOWTOS_DIR txcouchbase_search_ops.py
  assert_failure 134
}

@test "[howtos] - view_ops.py" {
  runExample $HOWTOS_DIR view_ops.py
  assert_success
}