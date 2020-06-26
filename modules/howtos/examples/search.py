import com.couchbase.client.core.error.CouchbaseException;
import com.couchbase.client.java.Bucket;
import com.couchbase.client.java.Cluster;
import com.couchbase.client.java.Collection;
import com.couchbase.client.java.analytics.AnalyticsResult;
import com.couchbase.client.java.json.JsonObject;
import com.couchbase.client.java.kv.MutationResult;
import com.couchbase.client.java.kv.MutationState;
import com.couchbase.client.java.search.HighlightStyle;
import com.couchbase.client.java.search.SearchOptions;
import com.couchbase.client.java.search.SearchQuery;
import com.couchbase.client.java.search.facet.SearchFacet;
import com.couchbase.client.java.search.result.ReactiveSearchResult;
import com.couchbase.client.java.search.result.SearchResult;
import com.couchbase.client.java.search.result.SearchRow;
import com.couchbase.client.java.search.sort.SearchSort;
import org.reactivestreams.Subscription;
import reactor.core.publisher.BaseSubscriber;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import static com.couchbase.client.java.search.SearchOptions.searchOptions;

public class Search {

  static Cluster cluster = Cluster.connect("localhost", "Administrator", "password");
  static Bucket bucket = cluster.bucket("travel-sample");
  static Collection collection = bucket.defaultCollection();

  public static void main(String... args) {

    {
      // #tag::simple[]
      try {
        final SearchResult result = cluster
          .searchQuery("index", SearchQuery.queryString("query"));

        for (SearchRow row : result.rows()) {
          System.out.println("Found row: " + row);
        }

        System.out.println("Reported total rows: "
          + result.metaData().metrics().totalRows());
      } catch (CouchbaseException ex) {
        ex.printStackTrace();
      }
      // #end::simple[]
    }

    {
      // #tag::squery[]
      final SearchResult result = cluster
        .searchQuery("my-index-name", SearchQuery.prefix("airports-"), searchOptions().fields("field-1"));

      for (SearchRow row : result.rows()) {
        System.out.println("Score: " + row.score());
        System.out.println("Document Id: " + row.id());

        // Also print fields that are included in the query
        System.out.println(row.fieldsAs(JsonObject.class));
      }
      // #end::squery[]
    }

    {
      // #tag::limit[]
      SearchResult result = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().skip(3).limit(4)
      );
      // #end::limit[]
    }

    {
      // #tag::ryow[]
      MutationResult mutationResult = collection.upsert("key", JsonObject.create());
      MutationState mutationState = MutationState.from(mutationResult.mutationToken().get());

      SearchResult searchResult = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().consistentWith(mutationState)
      );
      // #end::ryow[]
    }

    {
      // #tag::highlight[]
      SearchResult result = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().highlight(HighlightStyle.HTML, "field1", "field2")
      );
      // #end::highlight[]
    }

    {
      // #tag::sort[]
      SearchResult result = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().sort(SearchSort.byScore(), SearchSort.byField("field"))
      );
      // #end::sort[]
    }

    {
      // #tag::facets[]
      Map<String, SearchFacet> facets = new HashMap<>();
      facets.put("categories", SearchFacet.term("category", 5));

      SearchResult result = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().facets(facets)
      );
      // #end::facets[]
    }

    {
      // #tag::fields[]
      SearchResult result = cluster.searchQuery(
        "index",
        SearchQuery.queryString("query"),
        searchOptions().fields("field1", "field2")
      );
      // #end::fields[]
    }

    {
      // #tag::simplereactive[]
      Mono<ReactiveSearchResult> result = cluster
        .reactive()
        .searchQuery("index", SearchQuery.queryString("query"));

      result
        .flatMapMany(ReactiveSearchResult::rows)
        .subscribe(row -> System.out.println("Found row: " + row));
      // #end::simplereactive[]
    }

    {
      // #tag::backpressure[]
      Mono<ReactiveSearchResult> result = cluster
        .reactive()
        .searchQuery("index", SearchQuery.queryString("query"));

      result
        .flatMapMany(ReactiveSearchResult::rows)
        .subscribe(new BaseSubscriber<SearchRow>() {
          // Number of outstanding requests
          final AtomicInteger oustanding = new AtomicInteger(0);

          @Override
          protected void hookOnSubscribe(Subscription subscription) {
            request(10); // initially request to rows
            oustanding.set(10);
          }

          @Override
          protected void hookOnNext(SearchRow row) {
            process(row);
            if (oustanding.decrementAndGet() == 0) {
              request(10);
            }
          }
        });
      // #end::backpressure[]
    }
  }


  static void process(SearchRow value) {

  }

}
