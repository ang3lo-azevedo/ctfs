// SPDX-License-Identifier: MIT
// from https://github.com/The-Web3-Compass/30-days-of-solidity-submissions/blob/main/submissions/Kk/Day30/MiniDexPair.sol
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

contract MiniDex is ReentrancyGuard {
    address public immutable TOKEN_A;
    address public immutable TOKEN_B;
    uint256 public reserveA;
    uint256 public reserveB;

    event Swapped(address indexed user, address inputToken, uint256 inputAmount, address outputToken, uint256 outputAmount);

    constructor(address _tokenA, address _tokenB) {
        require(_tokenA != _tokenB, "Identical tokens");
        require(_tokenA != address(0) && _tokenB != address(0), "Zero address");

        TOKEN_A = _tokenA;
        TOKEN_B = _tokenB;
    }

    function _updateReserves() private {
        reserveA = IERC20(TOKEN_A).balanceOf(address(this));
        reserveB = IERC20(TOKEN_B).balanceOf(address(this));
    }

    function addLiquidity(uint256 amountA, uint256 amountB) external nonReentrant {
        require(amountA > 0 && amountB > 0, "Invalid amounts");
        IERC20(TOKEN_A).transferFrom(msg.sender, address(this), amountA);
        IERC20(TOKEN_B).transferFrom(msg.sender, address(this), amountB);

        _updateReserves();
    }

    function getAmountOut(uint256 inputAmount, address inputToken) public view returns (uint256 outputAmount) {
        require(inputToken == TOKEN_A || inputToken == TOKEN_B, "Invalid input token");
        bool isTokenA = inputToken == TOKEN_A;
        (uint256 inputReserve, uint256 outputReserve) = isTokenA ? (reserveA, reserveB) : (reserveB, reserveA);
        
        uint256 newInputReserve = inputReserve + inputAmount;
        uint256 newOutputReserve = (inputReserve * outputReserve) / newInputReserve;

        outputAmount = outputReserve - newOutputReserve;
    }

    function swap(uint256 inputAmount, address inputToken, uint256 deadline) external nonReentrant {
        require(inputAmount > 0, "Zero input");
        require(block.timestamp <= deadline, "Transaction expired");
        require(inputToken == TOKEN_A || inputToken == TOKEN_B, "Invalid token");
        address outputToken = inputToken == TOKEN_A ? TOKEN_B : TOKEN_A;
        uint256 outputAmount = getAmountOut(inputAmount, inputToken);
        require(outputAmount > 0, "Insufficient output");

        require(IERC20(inputToken).transferFrom(msg.sender, address(this), inputAmount));
        require(IERC20(outputToken).transfer(msg.sender, outputAmount));
        _updateReserves();
        emit Swapped(msg.sender, inputToken, inputAmount, outputToken, outputAmount);
    }

    function getReserves() external view returns (uint256, uint256) {
        return (reserveA, reserveB);
    }
}
