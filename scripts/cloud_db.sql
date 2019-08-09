--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
CREATE TABLE `config` (
  `broker_host` varchar(20) DEFAULT NULL,
  `broker_port` int(11) DEFAULT NULL,
  `sqlite_path` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `edge`
--

DROP TABLE IF EXISTS `edge`;
CREATE TABLE `edge` (
  `term_sn` varchar(30) NOT NULL COMMENT '边缘网络设备序列号',
  `config` text COMMENT '边缘网络设备配置',
  PRIMARY KEY (`term_sn`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `config`
--

INSERT INTO `config` VALUES ('127.0.0.1',1883,'./sqlite.db');
