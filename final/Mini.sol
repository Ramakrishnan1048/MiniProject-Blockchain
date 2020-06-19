
pragma solidity ^0.4.18;

contract Mini{
	struct Iot_data{
		bytes32 data;
	}
	
	mapping (uint => Iot_data) blocks;
	
	function addData(uint num, bytes32 data) public{
		uint blockId=num;
		blocks[blockId]= Iot_data(data);
	}
	
	function getData(uint blockId) public view returns(bytes32){
		return blocks[blockId].data;
	}
}
