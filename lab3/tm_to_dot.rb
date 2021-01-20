# Convert a Turing Machine description using the format described here
# (http://www.cs.binghamton.edu/~software/tm/tmdoc.html)
# to DOT.

require 'byebug'

filename = ARGV[0]

if !File.exist?(filename)
  puts "[error] File not found: #{filename}"
  exit(1)
end

lines = File.read(filename).split("\n")
lines = lines.map { |line| line.split("//")[0].strip }

# Line 1: ATM.
# Line 2: name of the machine. For assignments use name(s) and assignment number
# Line 3: all characters in the input alphabet, separated by spaces
# Line 4: all characters in the tape alphabet, separated by spaces

# Line 5: the number of tapes (N). They are numbered 0,…, N-1
num_tapes = lines[4].to_i

# Line 6: the number of tracks on tape 0 (T0)
# Line 7: the number of tracks on tape 1 (if N > 1) (T1)
# …
# Line N+5: the number of tracks on tape N-1 (TN-1)
idx = 5
idx += num_tapes

# Line N+6: 1 or 2, indicating tape 0 is 1-way or 2-way infinite tape
# Line N+7: 1 or 2, indicating tape 1 is 1-way or 2-way infinite
# …
# Line 2N+5: 1 or 2, indicating tape N-1 is 1-way or 2-way infinite
idx += num_tapes

# Line 2N+6: the initial state of the Turing machine
q_start = lines[idx]
idx += 1

# Line 2N+7: all the final states separated by spaces
q_final = lines[idx].split(/\s+/)
idx += 1

# Line 2N+8: first of a list of transition (see below)
# Line 2N+9: another transition
# …
# Line 2N+?: last of the list of transitions
# Last line: end. You must type the word "end" but it can be upper or lower case

colors = [
  '#26547C',
  '#EF476F',
  '#FFB20F',
  '#1A936F', #green
  '#555555'
]

colors_idx = (0..colors.size).to_a.sample

qfinals = q_final.map { |x| %Q{"#{x}"}}

puts %Q$digraph turing_machine {$
puts %Q$  "#{q_start}" [shape=doublecircle,style=filled,color="#cccccc"]$
puts %Q$  #{qfinals.join(',')} [shape=doublecircle,color="#555555",fontcolor="#555555"]$
puts %Q$  node [shape=circle,color="#555555",fontcolor="#555555"];$

while ((transition = lines[idx]) && !transition[/\AeNd\s*\z/i])

  err = false
  q_orig, tape_orig, q_next, tape_next, directions = transition.split(/\s+/)

  if q_orig.nil?     then STDERR.puts "[error] <q_orig> should not be empty"     ; err = 1 end
  if tape_orig.nil?  then STDERR.puts "[error] <tape_orig> should not be empty"  ; err = 1 end
  if q_next.nil?     then STDERR.puts "[error] <q_next> should not be empty"     ; err = 1 end
  if tape_next.nil?  then STDERR.puts "[error] <tape_next> should not be empty"  ; err = 1 end
  if directions.nil? then STDERR.puts "[error] <directions> should not be empty" ; err = 1 end

  Kernel.exit(1) if err

  color = colors[colors_idx]
  colors_idx = (colors_idx + 1) % (colors.size)
  puts %Q{  "#{q_orig}" -> "#{q_next}" [ label = "  #{tape_orig}, #{tape_next}, #{directions}  ", color="#{color}", fontcolor="#{color}"]}
  idx += 1

end

puts "}"
