import argparse
import json
import logging
import os
import platform
import re
import socket
import subprocess
import sys
import uuid
from datetime import datetime

try:
    import cpuinfo
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "py-cpuinfo"])
    import cpuinfo

try:
    import psutil
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

try:
    import git
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "GitPython"])
    import git

try:
    from pymongo import MongoClient
    from bson import ObjectId
except ModuleNotFoundError:
    # Do not install the bson package as it is incompatible with pymongo
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymongo"])
    from pymongo import MongoClient
    from bson import ObjectId

def create_logger(application_name: str, default_level=logging.NOTSET):
    # create logger
    logger = logging.getLogger(application_name)
    logger.setLevel(default_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def get_size(bytes_in, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_in < factor:
            return f"{bytes_in:.2f}{unit}{suffix}"
        bytes_in /= factor


def get_cpu_information(logger):
    logger.info("=" * 40 + "CPU Info" + "=" * 40)
    cpu_information = {}
    # number of cores
    logger.info("Physical cores:" + str(psutil.cpu_count(logical=False)))
    cpu_information["cores_physical"] = psutil.cpu_count(logical=False)

    logger.info("Total cores:" + str(psutil.cpu_count(logical=True)))
    cpu_information["cores_total"] = psutil.cpu_count(logical=True)

    # CPU frequencies
    cpufreq = psutil.cpu_freq()
    logger.info(f"Max Frequency: {cpufreq.max:.2f}Mhz")
    cpu_information["frequency_max"] = f"{cpufreq.max:.2f}Mhz"

    logger.info(f"Min Frequency: {cpufreq.min:.2f}Mhz")
    cpu_information["frequency_min"] = f"{cpufreq.min:.2f}Mhz"

    logger.info(f"Current Frequency: {cpufreq.current:.2f}Mhz")
    cpu_information["frequency_current"] = f"{cpufreq.current:.2f}Mhz"

    # CPU usage
    logger.info("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        logger.info(f"Core {i}: {percentage}%")
        cpu_information[f"core_usage_{i}"] = f"{percentage}%"
    logger.info(f"Total CPU Usage: {psutil.cpu_percent()}%")
    cpu_information[f"core_usage_all"] = f"{psutil.cpu_percent()}%"

    return cpu_information


def get_memory_information(logger):
    logger.info("=" * 40 + "Memory Information" + "=" * 40)
    memory_information = {}
    # get the memory details
    svmem = psutil.virtual_memory()
    logger.info(f"Total: {get_size(svmem.total)}")
    memory_information["total"] = f"{get_size(svmem.total)}"

    logger.info(f"Available: {get_size(svmem.available)}")
    memory_information["available"] = f"{get_size(svmem.available)}"

    logger.info(f"Used: {get_size(svmem.used)}")
    memory_information["used"] = f"{get_size(svmem.used)}"

    logger.info(f"Percentage: {svmem.percent}%")
    memory_information["percentage"] = f"{svmem.percent}%"

    logger.info("=" * 20 + "SWAP" + "=" * 20)
    swap_information = {}
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    logger.info(f"Total: {get_size(swap.total)}")
    swap_information["total"] = f"{get_size(swap.total)}"

    logger.info(f"Free: {get_size(swap.free)}")
    swap_information["free"] = f"{get_size(swap.free)}"

    logger.info(f"Used: {get_size(swap.used)}")
    swap_information["used"] = f"{get_size(swap.used)}"

    logger.info(f"Percentage: {swap.percent}%")
    swap_information["percentage"] = f"{swap.percent}%"

    memory_information["swap"] = swap_information
    return memory_information


def get_disk_information(logger) -> dict:
    logger.info("=" * 40 + "Disk Information" + "=" * 40)
    logger.info("Partitions and Usage:")
    disk_information = {}

    # get all disk partitions
    partitions = []
    for partition in psutil.disk_partitions():
        partition_dict = {}
        logger.info(f"=== Device: {partition.device} ===")
        partition_dict["device"] = partition.device
        logger.info(f"  Mountpoint: {partition.mountpoint}")
        partition_dict["mountpoint"] = partition.mountpoint
        logger.info(f"  File system type: {partition.fstype}")
        partition_dict["fstype"] = partition.fstype
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        logger.info(f"  Total Size: {get_size(partition_usage.total)}")
        partition_dict["total_size"] = f"{get_size(partition_usage.total)}"

        logger.info(f"  Used: {get_size(partition_usage.used)}")
        partition_dict["used"] = f"{get_size(partition_usage.used)}"

        logger.info(f"  Free: {get_size(partition_usage.free)}")
        partition_dict["free"] = f"{get_size(partition_usage.free)}"

        logger.info(f"  Percentage: {partition_usage.percent}%")
        partition_dict["percentage"] = f"{partition_usage.percent}%"

        partitions.append(partition_dict)
    disk_information["partitions"] = partitions
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    logger.info(f"Total read: {get_size(disk_io.read_bytes)}")
    disk_information["total_read"] = f"{get_size(disk_io.read_bytes)}"

    logger.info(f"Total write: {get_size(disk_io.write_bytes)}")
    disk_information["total_write"] = f"{get_size(disk_io.write_bytes)}"

    return disk_information


def get_network_information(logger) -> dict:
    logger.info("=" * 40 + "Network Information" + "=" * 40)
    network_information = {}

    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    interfaces = []
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            interface = {}
            logger.info(f"=== Interface: {interface_name} ===")
            interface["name"] = interface_name
            interface["address.family"] = str(address.family)

            if str(address.family) == 'AddressFamily.AF_INET':
                logger.info(f"  IP Address: {address.address}")
                interface["ip_address"] = address.address
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                logger.info(f"  MAC Address: {address.address}")
                interface["mac_address"] = address.address

            logger.info(f"  Netmask: {address.netmask}")
            logger.info(f"  Broadcast MAC: {address.broadcast}")
            interface["netmask"] = address.netmask
            interface["broadcast_ip"] = address.broadcast
            interfaces.append(interface)
    network_information["interfaces"] = interfaces
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    logger.info(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    logger.info(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    network_information["bytes_sent"] = f"{get_size(net_io.bytes_sent)}"
    network_information["bytes_received"] = f"{get_size(net_io.bytes_recv)}"
    return network_information


def get_installed_software(logger) -> list:
    logger.info("=" * 40 + "Installed Software Information" + "=" * 40)
    uname = platform.uname()
    software_list = []
    if uname.system == "Windows":
        data = subprocess.check_output(['wmic', 'product', 'get', 'name'])
        filter_list = ["'", "", "b'Name"]
        for program in str(data).split("\\r\\r\\n"):
            if program.strip() not in filter_list:
                logger.info(program.strip())
                software_list.append(program.strip())

    return software_list


def get_environment_parameter(logger) -> list:
    logger.info("=" * 40 + "Environment Parameter Information" + "=" * 40)
    parameter_list = []
    for item in os.environ:
        logger.info(f'{item}{" : "}{os.environ[item]}')
        parameter_list.append({item: os.environ[item]})

    return parameter_list


def get_system_information(logger, args) -> dict:
    system_information = {}
    if args.system_information:
        logger.info("=" * 40 + "System Information" + "=" * 40)
        uname = platform.uname()
        logger.info(f"System: {uname.system}")
        system_information["system"] = f"{uname.system}"

        logger.info(f"Node Name: {uname.node}")
        system_information["node_name"] = f"{uname.node}"

        logger.info(f"Release: {uname.release}")
        system_information["release"] = f"{uname.release}"

        logger.info(f"Version: {uname.version}")
        system_information["version"] = f"{uname.version}"

        logger.info(f"Machine: {uname.machine}")
        system_information["machine"] = f"{uname.machine}"

        logger.info(f"Processor: {uname.processor}")
        system_information["processor"] = f"{uname.processor}"

        logger.info(f"Processor: {cpuinfo.get_cpu_info()['brand_raw']}")
        system_information["processor_raw"] = f"{cpuinfo.get_cpu_info()['brand_raw']}"

        logger.info(f"Ip-Address: {socket.gethostbyname(socket.gethostname())}")
        system_information["ip_address"] = f"{socket.gethostbyname(socket.gethostname())}"

        logger.info(f"Mac-Address: {':'.join(re.findall('../../..', '%012x' % uuid.getnode()))}")
        system_information["mac_address"] = f"{':'.join(re.findall('../../..', '%012x' % uuid.getnode()))}"

        # Boot Time
        # https://psutil.readthedocs.io/en/latest/#psutil.boot_time
        logger.info("=" * 40 + "Boot Time" + "=" * 40)
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        logger.info(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")
        system_information["boot_time"] = f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
        system_information["boot_time_sec"] = boot_time_timestamp

        system_information["cpu"] = get_cpu_information(logger)
        system_information["memory"] = get_memory_information(logger)
        system_information["disk"] = get_disk_information(logger)
        system_information["network"] = get_network_information(logger)
        system_information["environment_parameter"] = get_environment_parameter(logger)
        system_information["software"] = get_installed_software(logger)
    return system_information


def create_argumentparser(program_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=program_name,
        description=f"The help of {program_name}",
        epilog="")
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    parser.add_argument(
        '-ewi', '--extract-workspace-information',
        help="Extract workspace information",
        action="store_const", dest="workspace_information", const=True,
        default=False,
    )
    parser.add_argument(
        '-esi', '--extract-system-information',
        help="Extract system information",
        action="store_const", dest="system_information", const=True,
        default=False,
    )
    parser.add_argument(
        '-json',
        help="Write the extracted information to a json file",
        action="store_const", dest="write_json_output", const=True,
        default=False,
    )
    parser.add_argument(
        '-json-pretty',
        help="Write the extracted information in a pretty format to a json file",
        action="store_const", dest="write_json_output_pretty", const=True,
        default=False,
    )
    parser.add_argument(
        '-json-filename',
        help="Define a specific name for the json output file",
        action="store", dest="json_filename",
        default="build-env.json",
    )
    parser.add_argument(
        '-conn', '--connection-string',
        help="Connection string to create a connection to the mongodb",
        action="store", dest="connection_string",
        default=os.getenv("MONGODB_CONNECTION_STRING", "mongodb://root:example@localhost:27017/")
    )
    parser.add_argument(
        '-db', '--database',
        help="Database name which to use",
        action="store", dest="database_name",
        default="test"
    )
    parser.add_argument(
        '-cn', '--collection-name',
        help="Collection name in the mongodb to send data to",
        action="store", dest="collection_name",
        default="build_env_info"
    )
    parser.add_argument(
        '-w', '--working-dir',
        help="Define the working directory",
        action="store", dest="working_directory",
        default=os.getcwd(),
    )
    parser.add_argument(
        '-f', '--filter',
        help="Define a filter for folder to ignore",
        action="store", dest="filter",
        default=[".git", ".idea", ".terraform", ".pytest_cache", ".github", ".circleci", ".expeditor", "packer_cache",
                 ".temp"],
    )
    return parser


def create_connection_to_mongodb(connection_string: str) -> MongoClient:
    return MongoClient(connection_string)


def close_connection_to_mongodb(client: MongoClient):
    client.close()


def select_database(client: MongoClient, database_name: str):
    return client[database_name]


def select_collection(database, collection_name: str):
    return database[collection_name]


def check_id(data):
    if "_id" in data:
        if isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
    else:
        data["_id"] = ObjectId()
    return data


def check_schema_version(data):
    if "schema_version" in data:
        if isinstance(data["_id"], str):
            data["schema_version"] = int(data["_id"])
    else:
        data["schema_version"] = 1
    return data


def apply_need_adaptations(data):
    data = check_id(data)
    data = check_schema_version(data)
    return data


def run_operation_on_collection(collection, is_replacement, data):
    if is_replacement:
        document_id = data.pop("_id")
        collection.replace_one({"_id": document_id}, data)
    else:
        collection.insert_one(data)


def check_directory(args, dirpath: str):
    folder_name = os.path.split(dirpath)[-1]
    if folder_name not in args.filter:
        print(dirpath)


def walk_through_directory(args, currentdir, levels_to_walk, current_level):
    for (dirpath, dirnames, filenames) in os.walk(currentdir):
        for dirname in dirnames:
            check_directory(args, dirname)
            if levels_to_walk == current_level:
                return
            else:
                folder_name = os.path.split(dirpath)[-1]
                if folder_name not in args.filter:
                    walk_through_directory(args, os.path.join(dirpath, dirname), levels_to_walk, current_level + 1)
    # else:
    #    print(f"The folder {folder_name} is in the ignore list")


def get_workspace_information(logger, args) -> dict:
    workspace_information = {}
    if args.workspace_information:
        logger.info("=" * 40 + "Workspace Information" + "=" * 40)
        levels_to_walk = 1
        current_level = 0
        walk_through_directory(args, args.working_directory, levels_to_walk, current_level)

    return workspace_information


def get_arguments():
    argument_parser = create_argumentparser(os.path.basename(__file__))
    if len(sys.argv) == 1:
        argument_parser.print_help(sys.stderr)
        sys.exit(1)
    return argument_parser.parse_args()


def write_information_to_json(args: argparse.Namespace, information: dict):
    if args.write_json_output or args.write_json_output_pretty:
        if args.write_json_output_pretty:
            indent = 4
        else:
            indent = None
        with open(os.path.join(args.working_directory, args.json_filename), 'w') as f:
            json.dump(information, f, indent=indent)


def send_information_to_mongo(args: argparse.Namespace, data: dict):
    client = create_connection_to_mongodb(args.connection_string)
    db = select_database(client, args.database_name)
    collection = select_collection(db, args.collection_name)
    data = apply_need_adaptations(data)
    run_operation_on_collection(collection, False, data)
    close_connection_to_mongodb(client)


def main():
    arguments = get_arguments()
    program_logger = create_logger(os.path.basename(__file__), arguments.loglevel)

    collected_information = {"system_information": get_system_information(program_logger, arguments),
                             "workspace_information": get_workspace_information(program_logger, arguments)}

    write_information_to_json(arguments, collected_information)

    send_information_to_mongo(arguments, collected_information)


if __name__ == "__main__":
    main()
