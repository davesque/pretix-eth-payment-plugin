#!/usr/bin/env python3

import argparse
import configparser
import logging
import os
import sys

basename = os.path.basename(sys.argv[0])

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=f'''
Update or create an ".ini" style config file from environment variables.

For example, invoking this script like this:

  PREFIX_DJANGO_DEBUG=false {basename} 'PREFIX_' my_cfg.cfg

...will create or update "my_cfg.cfg" to look like this:

  [django]
  debug=false

That is, of course, unless other env vars were present in the environment with
the prefix "PREFIX_".  If you want to disallow this, create a "whitelist.txt"
file with this content:

  PREFIX_DJANGO_DEBUG

...and invoke the command again as follows:

  PREFIX_DJANGO_DEBUG=false {basename} \\
    --whitelist-file='whitelist.txt' \\
    'PREFIX_' \\
    my_cfg.cfg
'''[1:-1],
)

parser.add_argument(
    'prefix',
    help=(
        'A prefix required in the names of all env vars used to update '
        'config keys.'
    ),
)
parser.add_argument(
    '--whitelist',
    help=(
        'The path of a file where each line is the name of an env var that '
        'should be used to update config keys.'
    ),
)
parser.add_argument(
    'config',
    help=(
        'The path of the config file to create or update.'
    ),
)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(message)s',
    )

    args = parser.parse_args()

    # Make config object
    config = configparser.RawConfigParser()
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config.read_file(f)
    except FileNotFoundError:
        pass

    # Read in whitelist if given
    if args.whitelist:
        with open(args.whitelist, 'r') as f:
            whitelist_lines = f.readlines()
            whitelist = set(j for j in (i.strip() for i in whitelist_lines) if j)
    else:
        whitelist = set()

    # Loop through all env vars and process them
    for var_name, var_value in os.environ.items():
        if whitelist and var_name not in whitelist:
            logging.info(f'  Ignoring {var_name} (not in whitelist)')
            continue

        if not var_name.startswith(args.prefix):
            logging.info(f'  Ignoring {var_name} (does not begin with prefix)')
            continue

        clipped_name = var_name[len(args.prefix):]
        parts = clipped_name.split('_', 1)
        section, option = parts[0].lower(), parts[1].lower()

        try:
            config.add_section(section)
        except (configparser.DuplicateSectionError, ValueError):
            pass

        logging.info(f'+ Adding "{section}.{option}={var_value}" from {var_name}')
        config.set(section, option, var_value)

    # Write updated config
    with open(args.config, 'w', encoding='utf-8') as f:
        config.write(f, space_around_delimiters=False)
