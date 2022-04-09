# cdnsift
Filter CDN IP addresses using automated and custom CIDR ranges.
This tool can help you filter IP addresses based on whether they are CDN addresses or not.

# How To Install?
1. Clone the repository
2. pip3 install -r requirements.txt

# What Are The Switches?
Switch | Explanation
--- | ---
**-i/--input** | Enter your IP list file path. (Default: - [pass from stdin])
**-v/--verbose** | Return IP ranges with CDN information.
**-d/--debug** | Show more debug messages.
**-du/--disable-update** | Do not update ranges.txt file.
**-o/--output** | Location of output file. (Don\'t use this switch if you wish to print the result to STDOUT)
**-r/--reverse** | Return result for IP addresses that are in CDN ranges.
**-a/--append** | Append a list of CDN ranges (One range per each line.)
<br>

# Usage Example?

1. Filter IP addresses from stdin and exclude CDN ranges<br>
cat ips.txt | python cdnsift.py

2. Filter IP addresses from file and include CDN ranges<br>
python cdnsift.py -r -i ips.txt

3. Filter IP addresses from file and do not update ranges.txt<br>
python cdnsift.py -i ips.txt -du

4. Filter IP addresses from file and save output to cdnFree_ips.txt<br>
python cdnsift.py -i ips.txt -o cdnFree_ips.txt
