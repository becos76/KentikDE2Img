# KentikDE2Img

This web app is leveraging Kentik's query TopXChart API endpoint to export Data Explorer time series charts into images or pdf files.
The query configuration is described in a json structure that is available to be copied from within the Kentik Portal. 
This json payload can be pasted into this app in order to get the respective chart in SVG, PNG or PDF files.

The app is containerized in a docker file, and once run it is server by default on port 8080.

Refer to [gemini's init file](./GEMINI.md) for more details and how to run.

## Kentik TopXChart API endpoint

Kentik Data Explorer time series charts can be exported as images (PNG or SVG), or PDF files.
This is accomplished by POSTing the DE query json to the following API endpoint and the response is the encoded file.

- https://api.kentik.com/api/v5/query/topxchart

> if your account is in Kentik EU cluster, the endpoint URL should be api.kentik.eu

In order to authenticate you must provide the following header parameters along with the calls
- X-CH-Auth-Email: <your portal email>
- X-CH-Auth-API-Token: <your API token>
- Content-Type: application/json

The json payload for the endpoint contains the query to run and the image type to be returned:
```
{
    "version":4,
    "queries":[
        {
            "bucket":"Left +Y Axis",
            "isOverlay":false,
            "query":{
                "all_devices":true,
                "aggregateTypes":["avg_bits_per_sec","p95th_bits_per_sec","max_bits_per_sec"],
                "aggregateThresholds":{"avg_bits_per_sec":0,"p95th_bits_per_sec":0,"max_bits_per_sec":0},
                ...
                }
        }
    ],
    "imageType":"<Choose svg or png or pdf>"
}

```

This is the sample payload returning the encoded image:
```json
{"dataUri":"data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pg0K ... "}
```
