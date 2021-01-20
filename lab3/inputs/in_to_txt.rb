##
# Convert human-readable test cases to MT format.
#

filename = ARGV[0]

if !File.exist?(filename)
  puts "[error] File not found: #{filename}"
  exit(1)
end

lines = File.read(filename).split("\n")

cases = lines.find_all { |x| x.start_with?('$') }.map { |x| x.split('//')[0].strip}

outfile = filename.sub(/\.in\z/, '.txt')

File.open(outfile, 'w') do |f|
  f.puts 1000
  f.puts cases.count
  f.puts cases.join("\n")
end

puts "Created input file: #{outfile}"
