import argparse

def main():
    parser = argparse.ArgumentParser(description="Add subdomain mappings to hosts file.")
    parser.add_argument("-s", "--subdomains", required=True, help="Comma-separated subdomains (e.g., api,app)")
    parser.add_argument("-u", "--url", required=True, help="Main domain (e.g., hello.com)")
    parser.add_argument("-p", "--rhost_ip", required=True, help="IP address of the remote host")

    args = parser.parse_args()

    subdomains = args.subdomains.split(",")  # Split the comma-separated list

    with open("/etc/hosts", "a") as hosts_file:
        for subdomain in subdomains:
            entry = f"{args.rhost_ip}   {subdomain.strip()}.{args.url}\n"
            hosts_file.write(entry)
            print(f"Added entry: {entry.strip()}")

if __name__ == "__main__":
    main()