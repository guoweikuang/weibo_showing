/*
Navicat MySQL Data Transfer

Source Server         : guoweikuang
Source Server Version : 50625
Source Host           : localhost:3306
Source Database       : weibo

Target Server Type    : MYSQL
Target Server Version : 50625
File Encoding         : 65001

Date: 2017-03-23 23:29:12
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for weibo_commment
-- ----------------------------
DROP TABLE IF EXISTS `weibo_commment`;
CREATE TABLE `weibo_commment` (
  `id` int(11) NOT NULL,
  `评论` text,
  `评论时间` varchar(255) DEFAULT NULL,
  `评论链接` varchar(255) DEFAULT NULL,
  `评论用户` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SET FOREIGN_KEY_CHECKS=1;
