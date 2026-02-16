#include <iostream>
using namespace std;


int main() {
    int pid = fork();
    cout << pid;

    return 0;
}