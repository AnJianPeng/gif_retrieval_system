#include <iostream>
#include <string>
#include <regex>
#include <fstream>

int main() {
	std::string line;
	std::ifstream inFile("tgif-v1.0.tsv");
	int lineCnt = 1;
	int totalCnt = 0;
	std::string target = R"(a boy )";
	//std::regex pattern("htt");

	std::ofstream outFile;
	outFile.open("boy.csv");
	while (std::getline(inFile, line)) {
		//std::cout << line << std::endl;
		if (line.find(target) != std::string::npos) {
			int tabPos = line.find('\t');
			std::string url = line.substr(0, tabPos);
			std::cout << "url is: " << url << std::endl;
			std::string desc = line.substr(tabPos + 1);
			std::cout << "description is: " << desc << std::endl;
			outFile << lineCnt << ", " << url << ", " << desc << "\n";
			totalCnt++;
		}
		lineCnt++;
	}
	std::cout << totalCnt << std::endl;
	return 1;
}