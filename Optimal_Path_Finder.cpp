#include <iostream>
#include <vector>
#include <climits>  
using namespace std;

// Function to print the grid with the path marked
void printGrid(const vector<vector<int>>& grid, const vector<vector<int>>& path) {
    int rows = grid.size();
    int cols = grid[0].size();
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (path[i][j] == 1) {
                cout << "* "; 
            } else {
                cout << grid[i][j] << " "; 
            }
        }
        cout << endl;
    }
}


int findOptimalPath(vector<vector<int>>& grid, vector<vector<int>>& dp, vector<vector<int>>& path, int i, int j) {
    int rows = grid.size();
    int cols = grid[0].size();
    
    // Base case: out of bounds or obstacle
    if (i < 0 || j < 0 || i >= rows || j >= cols || grid[i][j] == 1) {
        return INT_MAX; 
    }
    
    // If already computed, return
    if (dp[i][j] != -1) {
        return dp[i][j];
    }
    
    // Start point (top-left, assume cost 0)
    if (i == 0 && j == 0) {
        dp[i][j] = 0;
        path[i][j] = 1;  
        return 0;
    }
    
    // Recursive DP: min cost from left or up, plus current cell's cost (assume 1 for open, higher for obstacles if modified)
    int left = findOptimalPath(grid, dp, path, i, j-1);
    int up = findOptimalPath(grid, dp, path, i-1, j);
    
    int minCost = min(left, up);
    if (minCost == INT_MAX) {
        dp[i][j] = INT_MAX;
    } else {
        dp[i][j] = minCost + grid[i][j]; 
        path[i][j] = 1; 
    }
    
    return dp[i][j];
}

int main() {
    vector<vector<int>> grid = {
        {0, 0, 1, 0, 0},
        {0, 1, 0, 1, 0},
        {0, 0, 0, 0, 1},
        {1, 0, 1, 0, 0},
        {0, 0, 0, 0, 0}
    };
    
    int rows = grid.size();
    int cols = grid[0].size();
    

    vector<vector<int>> dp(rows, vector<int>(cols, -1));

    vector<vector<int>> path(rows, vector<int>(cols, 0));
    
  
    int cost = findOptimalPath(grid, dp, path, rows-1, cols-1);
    
    if (cost == INT_MAX) {
        cout << "No path found!" << endl;
    } else {
        cout << "Optimal path cost: " << cost << endl;
        cout << "Grid with path (* marked):" << endl;
        printGrid(grid, path);
    }
    
    return 0;
}
