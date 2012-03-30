// Skips BSON documents in a file without actually parsing the elements of the
// skipped documents.
#include <endian.h>

#include <stdint.h>
#include <fstream>
#include <iostream>

#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <boost/program_options.hpp>

using namespace std;

namespace po = boost::program_options;

void process(istream& is, unsigned int skip)
{
    for (unsigned i = 0; i < skip; ++i)
    {
        uint32_t size;
        streamsize read;
        read = is.readsome(reinterpret_cast<char*>(&size), sizeof(size));
        if (read < sizeof(size))
        {
            if (read)
            {
                cerr << "Unexpected end of BSON." << endl;
                exit(3);
            }
            cerr << "Reached end of file after skipping " << i << " documents." << endl;
            return;
        }
        if (is.fail() || !is.good())
        {
            cerr << "Read error after skipping " << i << " documents." << endl;
            exit (4);
        }
        size = le32toh(size);
        if (size < sizeof(size))
        {
            cerr << "Malformed BSON detected (invalid document size) after skipping " << i
                 << " documents." << endl;
            exit(5);
        }
        is.seekg(size - sizeof(size), ios_base::cur);
        if (is.fail())
        {
            cerr << "Malformed BSON detected (seek error) after skipping " << i << " documents."
                 << endl;
            exit(6);
        }
    }
    while (is.good())
    {
        char buf[4 * 1024 * 1024];
        streamsize read = is.readsome(buf, sizeof(buf));
        if (read)
            cout.write(buf, read);
        else
            break;
    }
}

struct UnsignedWrapper
{
    unsigned val;
};

void validate(boost::any& v, vector<string> const& values, UnsignedWrapper* target_type, int)
{
    string s = po::validators::get_single_string(values);
    boost::algorithm::trim(s);
    if (s.size() && s[0] != '-')
    {
        istringstream is(s);
        UnsignedWrapper value;
        is >> value.val;
        if (is.eof())
        {
            v = boost::any(value);
            return;
        }
    }
    throw po::validation_error(po::validation_error::invalid_option_value);
}

int main(int argc, char** argv) {
    UnsignedWrapper skip;
    string fname;
    po::options_description od;
    od.add_options()
        ("help", "Help message")
        ("skip",
         po::value<UnsignedWrapper>(&skip)->required(),
         "How many documents to skip.")
        ("input-file", po::value<string>(&fname),
         "Input file. If not specified, stdin will be used.")
        ;
    po::variables_map vm;
    try
    {
        po::store(po::command_line_parser(argc, argv).options(od).run(), vm);
        if (vm.count("help"))
        {
            cout << "Options:" << endl << od << endl;
            return 1;
        }
        vm.notify();
    }
    catch (po::error& e)
    {
        cerr << e.what() << endl;
        cout << "Options:" << endl << od << endl;
        return 2;
    }
    if (vm.count("input-file"))
    {
        ifstream ifs(vm.at("input-file").as<string>().c_str());
        process(ifs, skip.val);
    }
    else
    {
        process(cin, skip.val);
    }
	return 0;
}
