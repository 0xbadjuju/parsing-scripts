import sys
import re

username_regex = re.compile("User\s+:\s+(.+[^\$])\n$")
rid_regex = re.compile("RID\s+:\s+.+\s+\((\d+)\)")

ntlm_regex = re.compile("\s+NTLM\s+:\s+(.+)")
lm_regex = re.compile("\s+lm\s+-\s*(\d+):\s+(.+)")
end_regex = re.compile("Supplemental Credentials:")

blank_lm = "aad3b435b51404eeaad3b435b51404ee"

with open(sys.argv[2], "w") as output_file:
    with open(sys.argv[1]) as input_file:
        for line in input_file:
            username = ""
            rid = ""
            lm_hash = ""
            nt_hash = ""
            user_hash = ""
            rid_match = rid_regex.match(line)
            if rid_match:
                rid = rid_match.group(1)
                for line in input_file:
                    un_match = username_regex.match(line)
                    if un_match:
                        username = un_match.group(1)
                        for line in input_file:
                            nt_match = ntlm_regex.match(line)
                            if nt_match:
                                nt_hash = nt_match.group(1)
                                print username+":"+rid+":"+blank_lm+":"+nt_hash+":::"
                                output_file.write(username+":"+rid+":"+blank_lm+":"+nt_hash+":::\n")
                                break
                        break
