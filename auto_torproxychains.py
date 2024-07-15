import subprocess


def run_command(cmd):
    """Executes a shell command and handles errors."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}':\n{e.stderr}")


def install_and_configure_tor():
    """Installs Tor, Proxychains, and configures them."""

    # Update package lists and install Tor and Proxychains
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y tor proxychains")

    # Check Tor service status (optional)
    run_command("sudo service tor status")

    # Configure Proxychains
    with open("/etc/proxychains4.conf", "r") as file:
        lines = file.readlines()

    with open("/etc/proxychains4.conf", "w") as file:
        for line in lines:
            if line.startswith("dynamic_chain"):
                file.write("dynamic_chain\n")  # Enable dynamic chains
            elif line.startswith("strict_chain"):
                file.write("#strict_chain\n")  # Disable strict chains
            elif line.startswith('## Proxy DNS requests - no leak for DNS data'):
                file.write('Proxy DNS requests - no leak for DNS data')  # Enable Proxy DNS requests
            elif line.startswith("proxy_dns"):
                file.write("proxy_dns\n")  # Enable proxy DNS requests
            else:
                file.write(line)

        # Add SOCKS5 proxy configuration
        file.write("\nsocks5  127.0.0.1 9050\n")

    # Configure DNS resolver (optional - use Cloudflare DNS)
    with open("/usr/lib/proxychains3/proxyresolv", "w") as file:
        file.write("nameserver 1.1.1.1\n")

        # Create symbolic link for the resolver
    run_command("ln -s /usr/lib/proxychains3/proxyresolv /usr/bin/")

    # Restart Tor service
    run_command("sudo service tor restart")

    print("""An example of how to use the proxychains "proxychains nmap -sCV <ip>" """)
    print("Without running tor and proxychains it will use your real IP!!!")
    print("to test with proxychains, check this - https://github.com/macvk/dnsleaktest")


if __name__ == "__main__":
    install_and_configure_tor()
