##
# Compare MT log file with answers to grade an exercise.
#

require 'byebug'
require 'paint'

args = ARGV.join(" ")

# Input file.

md = args.match(/-i\s+([^ ]+)/)

if md.nil?
  puts "[error] Missing input file argument."
  exit(1)
end

in_file = md[1]

if !File.exist?(in_file)
  puts "[error] File not found: #{in_file}"
  exit(1)
end

# Output file.

md = args.match(/-o\s+([^ ]+)/)

if md.nil?
  puts "[error] Missing output file argument."
  exit(1)
end

out_file = md[1]

if !File.exist?(out_file)
  puts "[error] File not found: #{out_file}"
  exit(1)
end

# Parse test cases

test_lines = File.read(in_file).split("\n").select { |x| x.start_with?('$') }

cases = test_lines.map { |x| x.split(/(\/\/)|(%%)/) }
                  .map { |x| [x[0].strip, x[2].strip, x[4].strip] }

# Parse test results

report_lines = File.read(out_file).split("\n")

it_count  = 0
it_input  = nil
it_output = nil

idx = 0

while (idx < report_lines.size) do

  line = report_lines[idx]

  if (md = line.match(/\s*INPUT: (.*)/))

    # Find a corresponding input in the file
    it_input = md[1]
    input_case = cases.find { |x| x[0] == it_input }

    if input_case.nil?
      puts "[error] Could not find input #{it_input} in file #{in_file}"
      it_input = nil
    else
      # Found a result case
      it_count += 1
    end

  elsif (md = line.match(/\s*SNAPSHOT: FINAL TAPE\(S\):/))
    it_output = report_lines[idx+1]

    md       = report_lines[idx-1].match(/Stopped (.*) after Step: (\d+)/)
    answer   = md[1]
    step_num = md[2]

    puts "Number of steps: #{step_num}"

    if answer == "ACCEPTED"
      accepts = true
    elsif answer == "NOT Accepted"
      accepts = false
    else
      puts "[error] Invalid accept state: #{answer}"
      Kernel.exit(1)
    end

    tape_contents = it_output.match(/([^ ]+)\z/)[1]
    tape_contents = tape_contents.gsub('B', '')

    if it_input.nil?
      puts Paint["[warn] Found output without corresponding input", :yellow]
    else

      if step_num.to_i >= 1000 && !input_case[1].match(/FAIL/)
        puts Paint["[Fail] Test case #{input_case[0]} #{input_case[2]} is NOT correct.", :red, :bold]
        puts Paint["Machine was stuck in infinite loop (max steps achieved)", :red, :bold]
        puts
      elsif "#{input_case[1]}<read-head>" == tape_contents
        if accepts
          puts Paint["[Pass] Test case #{input_case[0]} #{input_case[2]} is correct.", :green]
          puts
        else
          puts Paint["[Fail] Test case #{input_case[0]} #{input_case[2]} is NOT correct.", :red, :bold]
          puts Paint["Expected machine to accept input, but it didn't", :red, :bold]
          puts
        end
      elsif input_case[1].match(/FAIL/) && !accepts
        puts Paint["[Pass] Test case #{input_case[0]} #{input_case[2]} is correct.", :green]
        puts Paint["Machine REJECTED input", :green]
        puts
      else
        puts Paint["[Fail] Test case #{input_case[0]} #{input_case[2]} is NOT correct.", :red, :bold]
        puts Paint["Expected: #{input_case[1]}<read-head>, got: #{tape_contents}", :red, :bold]
        puts
      end
    end
  end

  idx+=1

end
