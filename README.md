# Adminware Diagnostics

This is a prototype tool for allowing various management tools to non-root users. 

## Setup

- Add a sudo rule for adminware for user siteadmin

```
# On system with IPA 
ipa sudocmd-add "/PATH/TO/adminware/adminware.rb"
ipa sudorule-add RULENAME
ipa sudorule-add-user --groups=USERGROUP RULENAME
ipa sudorule-mod RULENAME --hostcat=''
ipa sudorule-add-allow-command --sudocmds  "/PATH/TO/adminware/adminware.rb" RULENAME
ipa sudorule-add-option RULENAME --sudooption '!authenticate'
ipa sudorule-add-host RULENAME --hostgroups=HOSTGROUP

# On systems without IPA
sudeoedit /etc/sudoers
    USERNAME ALL=NOPASSWD: /PATH/TO/adminware/adminware.rb
```

- Set permissions to 744 and ownership of root:root for `/PATH/TO/adminware/`

- Update and copy profile.d file into place

```
# Ensure the allowed group-name (currently siteadmin) and the path to the adminware installation are correct
vim /PATH/TO/adminware/etc/profile.d/alces-adminware.sh

cp /PATH/TO/adminware/etc/profile.d/alces-adminware.sh /etc/profile.d/
```
