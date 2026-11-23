# Inline review threads

Set `pr_id` to the `id` from `gh pr view`. Fetch every page of threads, including outdated ones. The first comment identifies the finding and the last shows who needs to respond.

```sh
gh api graphql --paginate -f id="$pr_id" -f query='
  query($id: ID!, $endCursor: String) {
    node(id: $id) {
      ... on PullRequest {
        reviewThreads(first: 100, after: $endCursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            id isResolved isOutdated path line originalLine
            root: comments(first: 1) { nodes { databaseId url author { __typename login } body } }
            latest: comments(last: 1) { nodes { author { __typename login } body } }
          }
        }
      }
    }
  }' --jq '.data.node.reviewThreads.nodes[] | select(.isResolved == false)'
```

Read the conversation at the root URL if earlier replies affect the decision. Skip a thread the PR author or you already answered unless a reviewer followed up.

If `gh pr view` returns 100 reviews or top-level comments, it may have stopped at the first page. For reviews, use `gh api --paginate repos/OWNER/REPO/pulls/NUMBER/reviews`. For conversation comments, use `gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments`.

To reply, take `repo` (owner/name) and `number` from the PR URL and `root_id` from the root comment's `databaseId`. Put the reply text in `reply`.

```sh
gh api "repos/$repo/pulls/$number/comments/$root_id/replies" -f body="$reply" --jq .html_url
```

Once GitHub returns the reply URL, resolve an answered bot thread using its GraphQL `id` as `thread_id`. Leave human threads open for their reviewers.

```sh
gh api graphql -f id="$thread_id" -f query='
  mutation($id: ID!) {
    resolveReviewThread(input: {threadId: $id}) { thread { isResolved } }
  }'
```
