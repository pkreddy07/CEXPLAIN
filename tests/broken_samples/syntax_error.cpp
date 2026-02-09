#include <iostream>
using namespace std;

extern int global_secret_key;

int main() {
    cout << "Key: " << global_secret_key << endl;
    return 0;
}