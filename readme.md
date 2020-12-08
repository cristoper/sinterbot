# Sinterbot2020

`sinterbot` is a little command line program (Python 3.5+) that helps to manage secret santa assignments. With `sinterbot` you can generate a valid secret santa assignment for a list of people and email each person their assigned gift recipient without ever revealing to anybody (including the operator of `sinterbot`) the full secret list of assignments.

For some of the theory and motivation behind `sinterbot`, see my weblog post [Deranged Sinterklaas: The Math and Algorithms of Secret Santa](https://catswhisker.xyz/log/2020/12/7/deranged_sinterklaas/)

`sinterbot` allows specifying some extra constraints such as minimum cycle length or a blacklist of people who should not be assigned to each other.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install sinterbot.

```bash
pip install sinterbot
```

## Usage

First create a config file with a list of participants' names and email addresses. The config file may also specify constraints for minimum cycle length and a blacklist. See [sample.conf](https://github.com/cristoper/sinterbot/blob/master/sample.conf) for a full example:

```xmas2020.conf
# xmas2020.conf
Santa A: user1@email.tld
Santa B: user2@email.tld
Santa C: user3@email.tld
Santa D: user4@email.tld
Santa E: user5@email.tld
```

The format is `Name: emailaddress`. Only the email addresses need to be unique.

Then run `sinterbot derange` to compute a valid assignment and save it to the config file:

```sh
$ sinterbot derange xmas2020.conf
Derangement info successfully added to config file.
Use `sinterbot send sample.conf -c smtp.conf` to send emails!
```

`sinterbot` will not allow you to re-derange a config file without passing the `--force` flag.

Now if you want you can view the secret santa assignments with `sinterbot view xmas2020.conf`. However, if you're a participant that would ruin the suprise for you! Instead you can email each person their assignment without ever seeing them yourself:

```sh
$ sinterbot send xmas2020.conf -c smtp.conf
Send message to user1@email.tld!
Send message to user2@email.tld!
Send message to user3@email.tld!
Send message to user4@email.tld!
Send message to user5@email.tld!
```

Before you can run the `sinterbot send` you need to create a file for your SMTP credentials:

```sh
# smtp.conf
#
# These settings are used to send the assignment emails. SMTPEmail will appear
# as the 'From:' address in the sent emails
#
# If SMTPUser is blank, SMTPEmail will be used as the user credentials.
#
# If SMTPPass is blank, the program will look for it in an environment variable
# called "sinter_smtp_pass" instead.
SMTPEmail: yourname@gmail.com
#SMTPUser:
SMTPPass: yourgmailpassword
SMTPServer: smtp.gmail.com
SMTPPort: 587
```  

(If you do not know what SMTP server to use but you have a gmail account, you can [use gmail's SMTP server](https://www.digitalocean.com/community/tutorials/how-to-use-google-s-smtp-server) using values like those exemplified above.)

To get full usage info run `sinterbot --help`. You can also pass `--help` to each subcommand:
```sh
$ sinterbot --help
usage: sinterbot [-h] {derange,check,send,view} ...

positional arguments:
  {derange,check,send,view}
    derange             Read .config file and add derangement information to
                        it.
    check               Check that the config file contains a valid
                        derangement
    send                Send every santa an email with the name of their
                        assigned recipient.
    view                Show the list of secret santa assignments.

optional arguments:
  -h, --help            show this help message and exit
```

## Feedback

Please feel free to use the Github [issues](https://github.com/cristoper/sinterbot/issues) to report bugs, ask questions, or make suggestions.

## Hacking

Clone repo:
```sh
$ git clone https://github.com/cristoper/sinterbot.git
$ cd sinterbot/
```

Run tests:
```sh
$ python -m unittest discover
```

Check types:
```sh
mypy sinterbot/*.py bin/*.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
