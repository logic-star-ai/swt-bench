## Running

To generate the website, run the following command.
```bash
python3 generate_index.py
``` 

Then serve it using the following command.
```bash
$ python3 -m http.server 8080
```

## Adding a new approach

To add a new approach, do the following:

1) Add the approach to `approaches.csv`
2) Add the organization to `orgs.csv`
3) Add the specific run(s) to `runs.csv` (i.e., verified and lite if applicable)