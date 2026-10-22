window.MEMORY_CASE = {
  "recorded_at": "2026-10-22T09:14:32.253949+00:00",
  "python": "3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]",
  "platform": "Windows-10-10.0.26200-SP0",
  "origin": "Research-built known-defect fixture; not upstream code or a Hermes/LLM evaluation.",
  "method": "Separate subprocesses; 800 unique keys for unbounded/bounded comparison, 800 repetitions of one key as a control; 64 KiB payload; gc.collect at each checkpoint; tracemalloc snapshot differences.",
  "metric": "Incremental Python-traced live allocations, not process RSS or native heap.",
  "fixture": "assets/memory-demo/cache_fixture.py",
  "fixture_sha256": "cd303deee25fd1794cddb84cbbf5b0a51404260d6de1353db8299aac77989090",
  "upstream_method_reference": "skills/prism-scan/references/optimize.md",
  "model_invoked": false,
  "cases": [
    {
      "mode": "unbounded",
      "samples": [
        {
          "requests": 0,
          "entries": 0,
          "traced_growth_bytes": 8,
          "traced_peak_bytes": 1920
        },
        {
          "requests": 200,
          "entries": 200,
          "traced_growth_bytes": 13140874,
          "traced_peak_bytes": 13142906
        },
        {
          "requests": 400,
          "entries": 400,
          "traced_growth_bytes": 26280998,
          "traced_peak_bytes": 26282890
        },
        {
          "requests": 600,
          "entries": 600,
          "traced_growth_bytes": 39411914,
          "traced_peak_bytes": 39413806
        },
        {
          "requests": 800,
          "entries": 800,
          "traced_growth_bytes": 52561270,
          "traced_peak_bytes": 52563162
        }
      ],
      "allocation_growth": [
        {
          "file": "cache_fixture.py",
          "line": 11,
          "source": "return bytearray(PAYLOAD_BYTES)",
          "growth_bytes": 52474400,
          "blocks": 1600
        },
        {
          "file": "cache_fixture.py",
          "line": 20,
          "source": "self.cache[key] = make_response()",
          "growth_bytes": 37288,
          "blocks": 2
        }
      ],
      "payload_allocation_line": 11,
      "fixture_growth_bytes_after_clear": 392,
      "payload_growth_bytes_after_clear": 0,
      "payload_bytes": 65536,
      "capacity": null
    },
    {
      "mode": "bounded",
      "samples": [
        {
          "requests": 0,
          "entries": 0,
          "traced_growth_bytes": 8,
          "traced_peak_bytes": 1920
        },
        {
          "requests": 200,
          "entries": 32,
          "traced_growth_bytes": 2106336,
          "traced_peak_bytes": 2176229
        },
        {
          "requests": 400,
          "entries": 32,
          "traced_growth_bytes": 2106652,
          "traced_peak_bytes": 2176377
        },
        {
          "requests": 600,
          "entries": 32,
          "traced_growth_bytes": 2106940,
          "traced_peak_bytes": 2176665
        },
        {
          "requests": 800,
          "entries": 32,
          "traced_growth_bytes": 2107228,
          "traced_peak_bytes": 2176953
        }
      ],
      "allocation_growth": [
        {
          "file": "cache_fixture.py",
          "line": 11,
          "source": "return bytearray(PAYLOAD_BYTES)",
          "growth_bytes": 2098976,
          "blocks": 64
        },
        {
          "file": "cache_fixture.py",
          "line": 34,
          "source": "self.cache[key] = make_response()",
          "growth_bytes": 4648,
          "blocks": 35
        },
        {
          "file": "cache_fixture.py",
          "line": 37,
          "source": "self.cache.popitem(last=False)",
          "growth_bytes": 48,
          "blocks": 1
        }
      ],
      "payload_allocation_line": 11,
      "fixture_growth_bytes_after_clear": 440,
      "payload_growth_bytes_after_clear": 0,
      "payload_bytes": 65536,
      "capacity": 32
    }
  ],
  "controls": {
    "repeated_key": {
      "mode": "repeated",
      "samples": [
        {
          "requests": 0,
          "entries": 0,
          "traced_growth_bytes": 8,
          "traced_peak_bytes": 1920
        },
        {
          "requests": 200,
          "entries": 1,
          "traced_growth_bytes": 66897,
          "traced_peak_bytes": 68761
        },
        {
          "requests": 400,
          "entries": 1,
          "traced_growth_bytes": 67213,
          "traced_peak_bytes": 69057
        },
        {
          "requests": 600,
          "entries": 1,
          "traced_growth_bytes": 67501,
          "traced_peak_bytes": 69345
        },
        {
          "requests": 800,
          "entries": 1,
          "traced_growth_bytes": 67789,
          "traced_peak_bytes": 69633
        }
      ],
      "allocation_growth": [
        {
          "file": "cache_fixture.py",
          "line": 11,
          "source": "return bytearray(PAYLOAD_BYTES)",
          "growth_bytes": 65593,
          "blocks": 2
        },
        {
          "file": "cache_fixture.py",
          "line": 20,
          "source": "self.cache[key] = make_response()",
          "growth_bytes": 560,
          "blocks": 2
        }
      ],
      "payload_allocation_line": 11,
      "fixture_growth_bytes_after_clear": 392,
      "payload_growth_bytes_after_clear": 0,
      "payload_bytes": 65536,
      "capacity": null
    }
  }
};
