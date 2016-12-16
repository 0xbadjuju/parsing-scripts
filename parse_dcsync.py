import sys
import re

command_regex = re.compile("mimikatz\(powershell\).+")
username_regex = re.compile("SAM Username\s+:\s+(.+)")
rid_regex = re.compile("Object Relative ID\s+:\s+(\d+)")
ntlm_regex = re.compile("\s+ntlm-\s*(\d+):\s+(.+)")
lm_regex = re.compile("\s+lm\s+-\s*(\d+):\s+(.+)")
end_regex = re.compile("Supplemental Credentials:")

blank_lm = "aad3b435b51404eeaad3b435b51404ee"

with open(sys.argv[2], "w") as output_file:
    with open(sys.argv[1]) as input_file:
        for line in input_file:
            command = command_regex.match(line)
            if command:
                username = ""
                rid = ""
                lm_array = [None]*100
                nt_array = [None]*100
                print command.group()

                for line in input_file:
                    un_match = username_regex.match(line)
                    if un_match:
                        username = un_match.group(1)

                        for line in input_file:
                            rid_match = rid_regex.match(line)
                            if rid_match:
                                rid = rid_match.group(1)

                                for line in input_file:

                                    ntlm_match = ntlm_regex.match(line)
                                    if ntlm_match:
                                        nt_array[int(ntlm_match.group(1))] = ntlm_match.group(2)

                                    lm_match = lm_regex.match(line)
                                    if lm_match:
                                        lm_array[int(lm_match.group(1))] = lm_match.group(2)
                                        user_hash = username + ":" + rid + ":" + lm_match.group(2) + ":" + nt_array[int(lm_match.group(1))] + ":::"
                                        print user_hash
                                        output_file.write(user_hash + "\n")
                                    end_match = end_regex.match(line)
                                    if end_match:
                                        break

                                if lm_array[0] is None:
                                    for index in nt_array:
                                        if index is None:
                                            break
                                        else:
                                            user_hash = username + ":" + rid + ":" + blank_lm + ":" + nt_array[int(lm_match.group(1))] + ":::"
                                            print user_hash
                                            output_file.write(user_hash + "\n")
                                break