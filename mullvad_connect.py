# All Rights Reserved.
# This code is proprietary and may not be used, copied, modified, or distributed without explicit permission from the owner.
import requests
import subprocess
import platform
import re
import sys


def get_mullvad_servers_by_country(country_name):
    url = "https://api.mullvad.net/www/relays/all/"
    response = requests.get(url)

    if response.status_code == 200:
        servers = response.json()

        country_servers = [server for server in servers if server['country_name'].lower() == country_name.lower()]

        if country_servers:
            return country_servers
        else:
            print(f"No servers found in {country_name}.")
            return []
    else:
        print("Error retrieving Mullvad server list.")
        return []


def get_all_countries():
    url = "https://api.mullvad.net/www/relays/all/"
    response = requests.get(url)

    if response.status_code == 200:
        servers = response.json()

        countries = set()

        for server in servers:
            countries.add(server['country_name'])

        return sorted(countries)
    else:
        print("Error retrieving Mullvad server list.")
        return []


def ping_server(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        output = subprocess.check_output(command, universal_newlines=True)
        match = re.search(r'time[=<]\s*(\d+\.?\d*)', output)
        if match:
            return float(match.group(1))
        else:
            return None
    except subprocess.CalledProcessError:
        return None


def connect_to_mullvad_server(hostname):
    hostname_array = hostname.split('-')
    check_protocol(hostname_array[2])
    try:
        command = ['mullvad', 'relay', 'set', 'location', hostname_array[0], hostname_array[1], hostname]
        subprocess.run(command, check=True)
    except Exception as set_relay_error:
        print(f"There has been an error in setting relay: \nCountry: {hostname_array[0]}\nCity: {hostname_array[1]}\nServer: {hostname}\nHas Failed with this connection error: {set_relay_error}")
    print(f"Mullvad Server Relay has been set.\nCountry: {hostname_array[0]}\nCity: {hostname_array[1]}\nServer: {hostname}")
    
    try:
        command = ['mullvad', 'connect']
        subprocess.run(command, check=True)
    except Exception as connection_error:
        print(f"Connection to: {hostname}\n\nHas Failed with this connection error: {connection_error}")
    print(f"Connected to {hostname} successfully.")
        
        
def check_protocol(protocol):
    if protocol == "ovpn":
        command = ['mullvad', 'relay', 'set', 'tunnel-protocol', 'openvpn']
        subprocess.run(command, check=True)
        print(f"OpenVPN Protocol has been detected, and set.")
    elif protocol == 'wg':
        command = ['mullvad', 'relay', 'set', 'tunnel-protocol', 'wireguard']
        subprocess.run(command, check=True)        
        print(f"WireGuard Protocol has been detected, and set.")


def find_fastest_server(_country, ping_threshold, protocol):
    servers = get_mullvad_servers_by_country(_country)
    server_ping_times = []
    
    mullvad_connection_check, cli_out = check_mullvad_connection()
    if mullvad_connection_check == True:
        acknowledge = input(f'{cli_out.capitalize()}, you will be disconnected before continuing.\n\nType "ok" to continue or "exit" to close : ')
        if acknowledge == "ok":
            command = ['mullvad', 'disconnect']
            subprocess.run(command, check=True)
        else:
            sys.exit()

    for server in servers:
        ip_address = server['ipv4_addr_in']
        country = server['country_name']
        city = server['city_name']
        hostname = server['hostname']
        tunneling_protocol = server['type']

        #print(f"Protocol from server: {tunneling_protocol}, Protocol from user: {protocol}")
        if protocol is None or protocol == tunneling_protocol:
            print(f"Pinging {hostname} ({city}, {country}) at {ip_address}...")
            ping_time = ping_server(ip_address)

            if ping_time is not None:
                print(f"{hostname} ping: {ping_time} ms \n")
                server_ping_times.append((hostname, country, city, ping_time))
            else:
                print(f"{hostname} is unreachable.\n")

    server_ping_times.sort(key=lambda x: x[3])

    if server_ping_times:
        fastest = server_ping_times[0]
        print("\nFastest server:")
        print(f"Hostname: {fastest[0]}, Country: {fastest[1]}, City: {fastest[2]}, Ping: {fastest[3]} ms")
        if protocol is None:
            print(f"If you intended to set a Tunneling Protocol. Please specifiy openvpn, wireguard or leave blank.")
        
        if fastest[3] <= ping_threshold:
            ask_user = input(f"Would you like to connect to {fastest[0]}? : ")
            if ask_user.lower() == "yes":
                print(f"\nConnecting to Server {fastest[0]} with a Ping of {fastest[3]} ms as the Ping is below {ping_threshold} ms.")
                connect_to_mullvad_server(fastest[0])
            else:
                print(f"\nUser Declined Connection to server: {fastest[0]}")
        else:
            print(f"\nServer {fastest[0]}'s Ping {fastest[3]} ms is above the threshold {ping_threshold} ms. Not connecting.")
    else:
        print("\nNo servers were reachable.")


def parse_country_ping_protocol(user_input):
    parts = user_input.split()

    if len(parts) == 0:
        raise ValueError("Country is required.")
    
    ping = 100
    protocol = None
    country = None

    for i, part in enumerate(parts):
        if part.isdigit():
            ping = int(part)
            country = " ".join(parts[:i])
            protocol = " ".join(parts[i + 1:])
            if protocol == "":
                protocol = None
            break
    else:
        country = " ".join(parts)

    if protocol:
        if "openvpn" in protocol.lower():
            protocol = "openvpn"
        elif "wireguard" in protocol.lower():
            protocol = "wireguard"
        else:
            print("No tunneling protocol detected. Defaulting to both protocols.")
            protocol = None

    return country, ping, protocol


def check_mullvad_installed():
    try:
        subprocess.run(['mullvad', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def check_mullvad_connection():
    try:
        result = subprocess.run(['mullvad', 'status'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip().lower()
        if "connected" in output and "disconnected" not in output:
            return True, output
        elif "disconnected" in output:
            return False, output
        else:
            print("Unexpected output from Mullvad CLI.")
            return False, output
    except subprocess.CalledProcessError as e:
        print(f"Error running Mullvad CLI: {e}")
        return False, str(e)
    except FileNotFoundError:
        print("Mullvad CLI is not installed or not found.")
        return False, "Mullvad CLI not installed or not found."


def prompt_user():
    print("Countries with Mullvad servers:")
    countries = get_all_countries()
    for country in countries:
        print(country)    
    
    while True:
        user_input = input("\nEnter Country [max_ping] [protocol] (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break

        try:
            country, ping, _protocol = parse_country_ping_protocol(user_input)
            print(f"Country: {country}, Max Ping: {ping}, Protocol: {_protocol}\n")
            find_fastest_server(country, ping, _protocol)
        except ValueError as e:
            print(f"Input Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    if check_mullvad_installed():
        mullvad_connection_check, cli_out = check_mullvad_connection()
        if mullvad_connection_check == True:
            acknowledge = input(f'{cli_out.capitalize()}, you will be disconnected before continuing.\n\nType "ok" to continue or "exit" to close : ')
            if acknowledge == "ok":
                command = ['mullvad', 'disconnect']
                subprocess.run(command, check=True)
            else:
                sys.exit()
                
        prompt_user()
    else:
        print("Mullvad CLI not installed. Please install it to use this script.")
