#!/usr/bin/expect -f
set timeout -1

foreach dir [glob -type d *] {

    if {$dir eq "TT"} {
        continue
    }

    puts "Processing directory: $dir"
    cd $dir

    set input_file "Ge_Ge_pair_${dir}.cmat"
    set output_file "Bw_Bw_${dir}.cmat"

    spawn cmat

    send "o $input_file\r"
    send "m2d\r"

    expect "Which indexes do you want to project"
    send "1 2\r"

    expect "Gates from file"
    send "N\r"

    expect "Low, High, Sign"
    send "55 55\r"

    expect "Low, High, Sign"
    send "\r"

    expect "OK"
    send "Y\r"

    expect "Want to symmetrize the extracted matrix"
    send "N\r"

    expect "File_name of the extracted matrix"
    send "$output_file\r"

    # Wait for main CMAT prompt
    expect "CMAT>"
    send "q\r"

    expect eof
    cd ..
}



