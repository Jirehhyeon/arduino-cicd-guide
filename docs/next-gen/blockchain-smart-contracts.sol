// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * 🛡️ Arduino DevOps 블록체인 보안 생태계
 * 스마트 컨트랙트로 IoT 디바이스 인증, 코드 검증, 배포 기록을 관리
 */

// 🔐 IoT 디바이스 NFT 인증 시스템
contract ArduinoDeviceRegistry is ERC721, Ownable, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    Counters.Counter private _deviceIds;
    
    struct DeviceInfo {
        string deviceType;        // "ESP32", "Arduino Uno", "Raspberry Pi"
        string firmwareHash;      // 현재 펌웨어의 IPFS 해시
        string hardwareSerial;    // 하드웨어 시리얼 번호
        address owner;            // 디바이스 소유자
        uint256 manufactureDate;  // 제조 날짜
        uint256 lastUpdate;       // 마지막 업데이트 시간
        bool isActive;            // 활성 상태
        string[] deploymentHistory; // 배포 기록
    }
    
    // 디바이스 ID => 디바이스 정보
    mapping(uint256 => DeviceInfo) public devices;
    
    // 하드웨어 시리얼 => 디바이스 ID (중복 방지)
    mapping(string => uint256) public serialToDeviceId;
    
    // 소유자 => 디바이스 ID 목록
    mapping(address => uint256[]) public ownerDevices;
    
    // 이벤트 정의
    event DeviceRegistered(uint256 indexed deviceId, string deviceType, address owner);
    event FirmwareUpdated(uint256 indexed deviceId, string oldHash, string newHash);
    event DeviceTransferred(uint256 indexed deviceId, address from, address to);
    event DeviceDeactivated(uint256 indexed deviceId, string reason);
    
    constructor() ERC721("ArduinoDeviceNFT", "ARDUINO") {}
    
    /**
     * 새 IoT 디바이스 등록
     */
    function registerDevice(
        string memory _deviceType,
        string memory _firmwareHash,
        string memory _hardwareSerial,
        address _owner
    ) external onlyOwner nonReentrant whenNotPaused returns (uint256) {
        require(bytes(_hardwareSerial).length > 0, "Serial number required");
        require(serialToDeviceId[_hardwareSerial] == 0, "Device already registered");
        
        _deviceIds.increment();
        uint256 newDeviceId = _deviceIds.current();
        
        // NFT 민팅
        _safeMint(_owner, newDeviceId);
        
        // 디바이스 정보 저장
        devices[newDeviceId] = DeviceInfo({
            deviceType: _deviceType,
            firmwareHash: _firmwareHash,
            hardwareSerial: _hardwareSerial,
            owner: _owner,
            manufactureDate: block.timestamp,
            lastUpdate: block.timestamp,
            isActive: true,
            deploymentHistory: new string[](0)
        });
        
        serialToDeviceId[_hardwareSerial] = newDeviceId;
        ownerDevices[_owner].push(newDeviceId);
        
        emit DeviceRegistered(newDeviceId, _deviceType, _owner);
        return newDeviceId;
    }
    
    /**
     * 펌웨어 업데이트 기록
     */
    function updateFirmware(
        uint256 _deviceId,
        string memory _newFirmwareHash,
        string memory _deploymentRecord
    ) external nonReentrant whenNotPaused {
        require(_exists(_deviceId), "Device does not exist");
        require(ownerOf(_deviceId) == msg.sender || owner() == msg.sender, "Not authorized");
        
        DeviceInfo storage device = devices[_deviceId];
        string memory oldHash = device.firmwareHash;
        
        device.firmwareHash = _newFirmwareHash;
        device.lastUpdate = block.timestamp;
        device.deploymentHistory.push(_deploymentRecord);
        
        emit FirmwareUpdated(_deviceId, oldHash, _newFirmwareHash);
    }
    
    /**
     * 디바이스 비활성화
     */
    function deactivateDevice(uint256 _deviceId, string memory _reason) 
        external nonReentrant whenNotPaused {
        require(_exists(_deviceId), "Device does not exist");
        require(ownerOf(_deviceId) == msg.sender || owner() == msg.sender, "Not authorized");
        
        devices[_deviceId].isActive = false;
        emit DeviceDeactivated(_deviceId, _reason);
    }
    
    /**
     * 디바이스 정보 조회
     */
    function getDeviceInfo(uint256 _deviceId) 
        external view returns (DeviceInfo memory) {
        require(_exists(_deviceId), "Device does not exist");
        return devices[_deviceId];
    }
    
    /**
     * 소유자의 모든 디바이스 조회
     */
    function getOwnerDevices(address _owner) 
        external view returns (uint256[] memory) {
        return ownerDevices[_owner];
    }
}

// 🔒 코드 검증 및 배포 스마트 컨트랙트
contract ArduinoCodeVerification is Ownable, ReentrancyGuard, Pausable {
    
    struct CodeSubmission {
        string ipfsHash;          // 소스코드 IPFS 해시
        address developer;        // 개발자 주소
        uint256 timestamp;        // 제출 시간
        string version;           // 버전 정보
        bool isVerified;          // 검증 완료 여부
        uint256 verificationScore; // 검증 점수 (0-100)
        string[] testResults;     // 테스트 결과
        mapping(address => bool) reviewers; // 코드 리뷰어들
        uint256 reviewCount;      // 리뷰 개수
    }
    
    struct DeploymentRecord {
        uint256 codeSubmissionId; // 코드 제출 ID
        uint256 deviceId;         // 대상 디바이스 ID
        address deployer;         // 배포자
        uint256 timestamp;        // 배포 시간
        bool isSuccessful;        // 배포 성공 여부
        string deploymentHash;    // 배포 해시
        uint256 gasUsed;          // 사용된 가스
    }
    
    using Counters for Counters.Counter;
    Counters.Counter private _submissionIds;
    Counters.Counter private _deploymentIds;
    
    // 코드 제출 기록
    mapping(uint256 => CodeSubmission) public codeSubmissions;
    
    // 배포 기록
    mapping(uint256 => DeploymentRecord) public deploymentRecords;
    
    // 개발자별 제출 기록
    mapping(address => uint256[]) public developerSubmissions;
    
    // 디바이스별 배포 기록
    mapping(uint256 => uint256[]) public deviceDeployments;
    
    // 검증자 권한 관리
    mapping(address => bool) public authorizedVerifiers;
    
    // 이벤트
    event CodeSubmitted(uint256 indexed submissionId, address developer, string ipfsHash);
    event CodeVerified(uint256 indexed submissionId, uint256 score, address verifier);
    event CodeDeployed(uint256 indexed deploymentId, uint256 submissionId, uint256 deviceId);
    event VerifierAdded(address verifier);
    event VerifierRemoved(address verifier);
    
    modifier onlyVerifier() {
        require(authorizedVerifiers[msg.sender] || owner() == msg.sender, "Not authorized verifier");
        _;
    }
    
    constructor() {
        authorizedVerifiers[msg.sender] = true;
    }
    
    /**
     * 코드 제출
     */
    function submitCode(
        string memory _ipfsHash,
        string memory _version,
        string[] memory _testResults
    ) external nonReentrant whenNotPaused returns (uint256) {
        require(bytes(_ipfsHash).length > 0, "IPFS hash required");
        
        _submissionIds.increment();
        uint256 newSubmissionId = _submissionIds.current();
        
        CodeSubmission storage submission = codeSubmissions[newSubmissionId];
        submission.ipfsHash = _ipfsHash;
        submission.developer = msg.sender;
        submission.timestamp = block.timestamp;
        submission.version = _version;
        submission.isVerified = false;
        submission.verificationScore = 0;
        submission.testResults = _testResults;
        submission.reviewCount = 0;
        
        developerSubmissions[msg.sender].push(newSubmissionId);
        
        emit CodeSubmitted(newSubmissionId, msg.sender, _ipfsHash);
        return newSubmissionId;
    }
    
    /**
     * 코드 검증
     */
    function verifyCode(
        uint256 _submissionId,
        uint256 _score,
        string[] memory _additionalTests
    ) external onlyVerifier nonReentrant whenNotPaused {
        require(_submissionId <= _submissionIds.current(), "Invalid submission ID");
        require(_score <= 100, "Score must be 0-100");
        
        CodeSubmission storage submission = codeSubmissions[_submissionId];
        require(!submission.reviewers[msg.sender], "Already reviewed by this verifier");
        
        submission.reviewers[msg.sender] = true;
        submission.reviewCount++;
        
        // 검증 점수 업데이트 (평균)
        submission.verificationScore = (submission.verificationScore + _score) / submission.reviewCount;
        
        // 추가 테스트 결과 병합
        for (uint i = 0; i < _additionalTests.length; i++) {
            submission.testResults.push(_additionalTests[i]);
        }
        
        // 검증 완료 기준: 점수 80 이상, 리뷰 2개 이상
        if (submission.verificationScore >= 80 && submission.reviewCount >= 2) {
            submission.isVerified = true;
        }
        
        emit CodeVerified(_submissionId, _score, msg.sender);
    }
    
    /**
     * 코드 배포 기록
     */
    function recordDeployment(
        uint256 _submissionId,
        uint256 _deviceId,
        bool _isSuccessful,
        string memory _deploymentHash,
        uint256 _gasUsed
    ) external nonReentrant whenNotPaused returns (uint256) {
        require(_submissionId <= _submissionIds.current(), "Invalid submission ID");
        require(codeSubmissions[_submissionId].isVerified, "Code not verified");
        
        _deploymentIds.increment();
        uint256 newDeploymentId = _deploymentIds.current();
        
        deploymentRecords[newDeploymentId] = DeploymentRecord({
            codeSubmissionId: _submissionId,
            deviceId: _deviceId,
            deployer: msg.sender,
            timestamp: block.timestamp,
            isSuccessful: _isSuccessful,
            deploymentHash: _deploymentHash,
            gasUsed: _gasUsed
        });
        
        deviceDeployments[_deviceId].push(newDeploymentId);
        
        emit CodeDeployed(newDeploymentId, _submissionId, _deviceId);
        return newDeploymentId;
    }
    
    /**
     * 검증자 추가
     */
    function addVerifier(address _verifier) external onlyOwner {
        authorizedVerifiers[_verifier] = true;
        emit VerifierAdded(_verifier);
    }
    
    /**
     * 검증자 제거
     */
    function removeVerifier(address _verifier) external onlyOwner {
        authorizedVerifiers[_verifier] = false;
        emit VerifierRemoved(_verifier);
    }
    
    /**
     * 코드 제출 정보 조회
     */
    function getCodeSubmission(uint256 _submissionId) 
        external view returns (
            string memory ipfsHash,
            address developer,
            uint256 timestamp,
            string memory version,
            bool isVerified,
            uint256 verificationScore,
            string[] memory testResults,
            uint256 reviewCount
        ) {
        require(_submissionId <= _submissionIds.current(), "Invalid submission ID");
        
        CodeSubmission storage submission = codeSubmissions[_submissionId];
        return (
            submission.ipfsHash,
            submission.developer,
            submission.timestamp,
            submission.version,
            submission.isVerified,
            submission.verificationScore,
            submission.testResults,
            submission.reviewCount
        );
    }
    
    /**
     * 디바이스 배포 기록 조회
     */
    function getDeviceDeployments(uint256 _deviceId) 
        external view returns (uint256[] memory) {
        return deviceDeployments[_deviceId];
    }
    
    /**
     * 개발자 제출 기록 조회
     */
    function getDeveloperSubmissions(address _developer) 
        external view returns (uint256[] memory) {
        return developerSubmissions[_developer];
    }
}

// 🎖️ 개발자 평판 및 인센티브 시스템
contract ArduinoDeveloperReputation is Ownable, ReentrancyGuard {
    
    struct Developer {
        string nickname;
        uint256 totalSubmissions;
        uint256 verifiedSubmissions;
        uint256 successfulDeployments;
        uint256 totalReputationScore;
        uint256 totalEarnings;
        bool isCertified;
        string[] specializations; // ["IoT", "AI", "Blockchain", "Security"]
        mapping(string => uint256) skillLevels; // 기술별 레벨 (0-100)
    }
    
    mapping(address => Developer) public developers;
    mapping(address => bool) public registeredDevelopers;
    
    // 평판 토큰 (ERC-20)
    string public constant name = "Arduino Reputation Token";
    string public constant symbol = "ART";
    uint8 public constant decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    
    // 이벤트
    event DeveloperRegistered(address indexed developer, string nickname);
    event ReputationAwarded(address indexed developer, uint256 amount, string reason);
    event SkillLevelUpdated(address indexed developer, string skill, uint256 level);
    event CertificationGranted(address indexed developer);
    
    constructor() {
        totalSupply = 1000000 * 10**decimals; // 100만 토큰
        balances[owner()] = totalSupply;
    }
    
    /**
     * 개발자 등록
     */
    function registerDeveloper(
        string memory _nickname,
        string[] memory _specializations
    ) external nonReentrant {
        require(!registeredDevelopers[msg.sender], "Already registered");
        require(bytes(_nickname).length > 0, "Nickname required");
        
        Developer storage dev = developers[msg.sender];
        dev.nickname = _nickname;
        dev.specializations = _specializations;
        dev.isCertified = false;
        
        registeredDevelopers[msg.sender] = true;
        
        // 등록 보너스
        _awardReputation(msg.sender, 100 * 10**decimals, "Registration bonus");
        
        emit DeveloperRegistered(msg.sender, _nickname);
    }
    
    /**
     * 평판 점수 부여 (검증된 제출, 성공적 배포 시)
     */
    function awardReputation(
        address _developer,
        uint256 _amount,
        string memory _reason
    ) external onlyOwner {
        _awardReputation(_developer, _amount, _reason);
    }
    
    function _awardReputation(
        address _developer,
        uint256 _amount,
        string memory _reason
    ) internal {
        require(registeredDevelopers[_developer], "Developer not registered");
        
        developers[_developer].totalReputationScore += _amount;
        developers[_developer].totalEarnings += _amount;
        
        // 토큰 전송
        _transfer(owner(), _developer, _amount);
        
        emit ReputationAwarded(_developer, _amount, _reason);
    }
    
    /**
     * 기술 레벨 업데이트
     */
    function updateSkillLevel(
        address _developer,
        string memory _skill,
        uint256 _level
    ) external onlyOwner {
        require(registeredDevelopers[_developer], "Developer not registered");
        require(_level <= 100, "Level must be 0-100");
        
        developers[_developer].skillLevels[_skill] = _level;
        
        emit SkillLevelUpdated(_developer, _skill, _level);
        
        // 높은 레벨 달성 시 인증 검토
        _checkCertificationEligibility(_developer);
    }
    
    /**
     * 인증 자격 검토
     */
    function _checkCertificationEligibility(address _developer) internal {
        Developer storage dev = developers[_developer];
        
        // 인증 기준: 평판 점수 10,000 이상, 검증된 제출 10개 이상, 성공적 배포 5개 이상
        if (dev.totalReputationScore >= 10000 * 10**decimals &&
            dev.verifiedSubmissions >= 10 &&
            dev.successfulDeployments >= 5 &&
            !dev.isCertified) {
            
            dev.isCertified = true;
            
            // 인증 보너스
            _awardReputation(_developer, 5000 * 10**decimals, "Certification bonus");
            
            emit CertificationGranted(_developer);
        }
    }
    
    /**
     * ERC-20 토큰 전송
     */
    function _transfer(address _from, address _to, uint256 _amount) internal {
        require(_from != address(0), "Transfer from zero address");
        require(_to != address(0), "Transfer to zero address");
        require(balances[_from] >= _amount, "Insufficient balance");
        
        balances[_from] -= _amount;
        balances[_to] += _amount;
    }
    
    function transfer(address _to, uint256 _amount) external returns (bool) {
        _transfer(msg.sender, _to, _amount);
        return true;
    }
    
    function balanceOf(address _account) external view returns (uint256) {
        return balances[_account];
    }
    
    /**
     * 개발자 정보 조회
     */
    function getDeveloperInfo(address _developer) 
        external view returns (
            string memory nickname,
            uint256 totalSubmissions,
            uint256 verifiedSubmissions,
            uint256 successfulDeployments,
            uint256 totalReputationScore,
            bool isCertified,
            string[] memory specializations
        ) {
        require(registeredDevelopers[_developer], "Developer not registered");
        
        Developer storage dev = developers[_developer];
        return (
            dev.nickname,
            dev.totalSubmissions,
            dev.verifiedSubmissions,
            dev.successfulDeployments,
            dev.totalReputationScore,
            dev.isCertified,
            dev.specializations
        );
    }
    
    /**
     * 기술 레벨 조회
     */
    function getSkillLevel(address _developer, string memory _skill) 
        external view returns (uint256) {
        require(registeredDevelopers[_developer], "Developer not registered");
        return developers[_developer].skillLevels[_skill];
    }
}