/*
SQLyog Ultimate v13.1.1 (64 bit)
MySQL - 8.0.36 : Database - product_pricing_system
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`product_pricing_system` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `product_pricing_system`;

/*Table structure for table `admin` */

DROP TABLE IF EXISTS `admin`;

CREATE TABLE `admin` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '璐﹀彿',
  `password` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '瀵嗙爜',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '鐢ㄦ埛鍚?,
  `avatar` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '澶村儚',
  `role` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '瑙掕壊',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='绠＄悊鍛樹俊鎭?;

/*Data for the table `admin` */

insert  into `admin`(`id`,`username`,`password`,`name`,`avatar`,`role`) values
(1,'椋炶捣','1','瓒呯骇绠＄悊鍛?,'/files/download/榛樿绠＄悊鍛樺ご鍍?jpg','绠＄悊鍛?);

/*Table structure for table `feedback` */

DROP TABLE IF EXISTS `feedback`;

CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '鍙嶉id',
  `userId` int DEFAULT NULL COMMENT '鐢ㄦ埛id',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '鐢ㄦ埛鍚嶇О',
  `content` varchar(1000) DEFAULT NULL COMMENT '鍙嶉鍐呭',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '鍙嶉鏃堕棿',
  `status` tinyint DEFAULT '0' COMMENT '鐘舵€侊細0-鏈锛?-宸茶',
  `reply` varchar(1000) DEFAULT NULL COMMENT '绠＄悊鍛樺洖澶?,
  `reply_time` datetime DEFAULT NULL COMMENT '鍥炲鏃堕棿',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`userId`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='鐢ㄦ埛鍙嶉琛?;

/*Data for the table `feedback` */

/*Table structure for table `pricing_record` */

DROP TABLE IF EXISTS `pricing_record`;

CREATE TABLE `pricing_record` (
  `id` varchar(64) NOT NULL COMMENT '璁板綍ID',
  `image_path` varchar(255) NOT NULL COMMENT '妫€娴嬪浘鐗囪矾寰?,
  `total_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '鎬讳环鏍?,
  `item_count` int NOT NULL DEFAULT '0' COMMENT '鍟嗗搧鎬绘暟閲?,
  `detection_duration` float NOT NULL COMMENT '妫€娴嬬敤鏃?ms)',
  `execute_duration` float NOT NULL COMMENT '鎵ц鏃堕暱(s)',
  `create_time` datetime NOT NULL COMMENT '鍒涘缓鏃堕棿',
  `create_user_id` varchar(64) DEFAULT NULL COMMENT '鍒涘缓鐢ㄦ埛ID',
  `create_user_name` varchar(100) DEFAULT NULL COMMENT '鍒涘缓鐢ㄦ埛鍚嶇О',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='璁′环璁板綍琛?;

/*Data for the table `pricing_record` */

insert  into `pricing_record`(`id`,`image_path`,`total_price`,`item_count`,`detection_duration`,`execute_duration`,`create_time`,`create_user_id`,`create_user_name`) values
('3c86cdf35c984b95b46e883c248483db','/results/images/uploaded_image14476409249919320453.jpg',37.15,10,13.1505,3.61293,'2025-04-14 02:54:19',NULL,NULL),
('4a2f8ddee5e341069aa2550124e4b888','/results/images/uploaded_image8868322176948371706.jpg',41.90,6,27.4931,5.58718,'2025-04-14 04:39:34',NULL,NULL),
('58a2c534320f46d6be05e0d649858e12','/results/images/uploaded_image6656362461327452412.jpg',24.45,5,16.6038,3.75863,'2025-04-14 16:51:46',NULL,NULL),
('69bdf4cf9def4d81b921d31b54b9a912','/results/images/uploaded_image2790561760370882676.jpg',47.30,10,13.0502,3.49078,'2025-04-15 03:20:47',NULL,NULL),
('8779df7728ad4c229dd8e374ccbe0bf1','/results/images/uploaded_image17281519419827576003.jpg',32.85,6,15.3788,4.88773,'2025-04-14 01:34:47',NULL,NULL),
('969c16f6d381450cb7cb583baa84f638','/results/images/uploaded_image11532120114610634334.jpg',39.80,9,12.8974,2.68961,'2025-04-14 16:54:50',NULL,NULL),
('d5e2e40286734423869ea226682ddde5','/results/images/uploaded_image3320354160859820398.jpg',25.40,6,18.7718,4.51999,'2025-04-14 01:34:02',NULL,NULL);

/*Table structure for table `pricing_record_item` */

DROP TABLE IF EXISTS `pricing_record_item`;

CREATE TABLE `pricing_record_item` (
  `id` varchar(64) NOT NULL COMMENT '椤圭洰ID',
  `record_id` varchar(64) NOT NULL COMMENT '鍏宠仈鐨勮褰旾D',
  `name` varchar(100) NOT NULL COMMENT '鍟嗗搧鍚嶇О',
  `count` int NOT NULL DEFAULT '1' COMMENT '鍟嗗搧鏁伴噺',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '鍟嗗搧鍗曚环',
  PRIMARY KEY (`id`),
  KEY `idx_record_id` (`record_id`),
  CONSTRAINT `pricing_record_item_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `pricing_record` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `pricing_record_item` */

insert  into `pricing_record_item`(`id`,`record_id`,`name`,`count`,`price`) values
('01cfe134b78e4e0db821019354890fae','3c86cdf35c984b95b46e883c248483db','鍢夐】濞佸寲楗煎共鏌犳鍛?0g',3,2.00),
('0c0541113ece486db67c907cb8914d62','3c86cdf35c984b95b46e883c248483db','閾堕弓妞板ザ鐕曢害绮?80g',1,3.50),
('1af586a352e74b8294aace3573fc8073','969c16f6d381450cb7cb583baa84f638','鍠滃姏鍟ら厭500ml',1,6.90),
('2c6358c8611946a5a4ec9e0d86b74862','969c16f6d381450cb7cb583baa84f638','缁磋揪濠村効150x3',1,6.10),
('393e2baaa0fd4646a419bb1ad43556c4','4a2f8ddee5e341069aa2550124e4b888','鎯犲疁鑵版灉160g',1,21.40),
('3d6aad10208c4e6a918eed44455dee8c','969c16f6d381450cb7cb583baa84f638','鑿滃洯灏忛ゼ80g',3,1.60),
('3e106ba274a7459dbe2ff25c323b4b1f','d5e2e40286734423869ea226682ddde5','蹇冪浉鍗板皬榛勪汉150x3',3,2.20),
('42e264b32b8b466bbbed6cff9421c2ad','69bdf4cf9def4d81b921d31b54b9a912','QQ鏄熷潎鑶冲ザ125ml',1,3.00),
('4cee793a1ff84ad3abc501e3b5170239','69bdf4cf9def4d81b921d31b54b9a912','闃垮皵鍗戞柉鐒﹂鐗涘ザ鍛崇‖绯?5g',2,2.50),
('52cdcf0cc3d94d37920e4a80f4175779','969c16f6d381450cb7cb583baa84f638','鐧惧▉鍟ら厭600ml',2,6.00),
('55f9863432914d889f00213eef79cc2f','8779df7728ad4c229dd8e374ccbe0bf1','濡欒剢瑙掗瓟鍔涚偔鐑у懗65g',1,6.55),
('565d47fb4e79496292d232a88c6c9f31','69bdf4cf9def4d81b921d31b54b9a912','鍗庝赴楦¤倝涓夐矞浼婇潰87g',1,2.00),
('78b020727db64722bcaf63d29a3d9a27','3c86cdf35c984b95b46e883c248483db','澹姏鏋惰姳鐢熷す蹇冨阀鍏嬪姏51g',3,3.30),
('85210f2178b94194a611a8c573f7215d','58a2c534320f46d6be05e0d649858e12','娲芥唇鍑夎尪鐡滃瓙150g',2,6.70),
('8e12678929e64ad689ccaf1977a5e319','4a2f8ddee5e341069aa2550124e4b888','搴峰笀鍌呰棨妞掔墰鑲夐潰85g',3,4.50),
('8ee87e63de7f476980d9583a573952e7','d5e2e40286734423869ea226682ddde5','鍠滃姏鍟ら厭500ml',2,6.90),
('929ad3b042c44fdfa596ad03ec7e611e','8779df7728ad4c229dd8e374ccbe0bf1','瀹濋紟澶╅奔闄堥吙绫抽唻245ml',1,5.60),
('9641426ed23246c98c894c3fca5a1e08','69bdf4cf9def4d81b921d31b54b9a912','娓呴鍘熸湪绾搧閲戣100x3',3,1.80),
('9838cafc9d4a4300bfe26fa479c160b8','3c86cdf35c984b95b46e883c248483db','濡欒剢瑙掗瓟鍔涚偔鐑у懗65g',1,6.55),
('a07d903142b3470cb72b50e21f1882bd','69bdf4cf9def4d81b921d31b54b9a912','鏂扮枂鍜岀敯婊╂灒454g',2,6.00),
('adced316bf134c6c86a6a2282da7765c','69bdf4cf9def4d81b921d31b54b9a912','閮戒箰鑿犺悵鍧?67g',1,19.90),
('c273ec03117a47ada3c44566545b201a','3c86cdf35c984b95b46e883c248483db','瀹濋紟澶╅奔闄堥吙绫抽唻245ml',2,5.60),
('c881bf2e400748e5afc46a4b8031ce57','969c16f6d381450cb7cb583baa84f638','鑼舵淳鐜懓鑽旀灊绾㈣尪500ml',2,5.00),
('d1813e37074d4a02b74f58a41480a86b','d5e2e40286734423869ea226682ddde5','鑼舵淳鐜懓鑽旀灊绾㈣尪500ml',1,5.00),
('d40ca890780347b6bfca7358dc679074','58a2c534320f46d6be05e0d649858e12','鐧惧姏婊嬫捣鑻斿懗60g',2,4.20),
('d6d9862937074ff49a525fc723460671','58a2c534320f46d6be05e0d649858e12','鏂戝竷100x3',1,2.65),
('d8d493ab2e00494daf83f7683b560095','4a2f8ddee5e341069aa2550124e4b888','鐖变埂浜插敱鐗囬潰鍖?0g',2,3.50),
('f7e0c07f884b406d81c2c540cef2bb5a','8779df7728ad4c229dd8e374ccbe0bf1','浼婂埄鏃╅濂?50ml',1,2.70),
('fcdd96c257504e5f9abb1297cd111400','8779df7728ad4c229dd8e374ccbe0bf1','鐧惧▉鍟ら厭600ml',3,6.00);

/*Table structure for table `product` */

DROP TABLE IF EXISTS `product`;

CREATE TABLE `product` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '鍟嗗搧涓籭d',
  `image` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '鍟嗗搧鍥剧墖',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '鍟嗗搧鍚嶇О',
  `category_id` int DEFAULT NULL COMMENT '鍟嗗搧灞炵被id',
  `price` double DEFAULT NULL COMMENT '鍟嗗搧浠锋牸',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '澶囨敞',
  `sales` int DEFAULT '0' COMMENT '鍟嗗搧閿€鍞噺',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `product` */

insert  into `product`(`id`,`image`,`name`,`category_id`,`price`,`remark`,`sales`) values
(1,'/files/download/6909409012031_camera2-20.jpg','涓婂ソ浣宠嵎鍏拌眴55g',NULL,3.5,NULL,0),
(2,'/files/download/6901845043112_camera2-19.jpg','鑿滃洯灏忛ゼ80g',NULL,1.6,NULL,6),
(3,'/files/download/6909409012024_camera2-20.jpg','涓婂ソ浣抽矞铏剧墖40g',NULL,3.5,NULL,0),
(4,'/files/download/6926265388100_camera2-20.jpg','涓婂ソ浣宠煿鍛抽€告棌40g',NULL,4.2,NULL,0),
(5,'/files/download/6924743920330_camera2-20.jpg','濡欒剢瑙掗瓟鍔涚偔鐑у懗65g',NULL,6.55,NULL,5),
(6,'/files/download/6920912342002_camera2-20.jpg','鐩肩浖鐑х儰鐗涙帓鍛冲潡105g',NULL,4.8,NULL,0),
(7,'/files/download/6926265301024_camera2-20.jpg','涓婂ソ浣抽矞铏炬潯40g',NULL,4.6,NULL,1),
(8,'/files/download/6909409040799_camera2-19.jpg','涓婂ソ浣虫磱钁卞湀40g',NULL,5.6,NULL,3),
(9,'/files/download/6926265301130_camera2-20.jpg','涓婂ソ浣虫棩寮忛奔鏋滄捣鑻斿懗50g',NULL,4.5,NULL,0),
(10,'/files/download/6924743913721_camera2-20.jpg','濂囧鏃ュ紡鐗涙帓鍛?0g',NULL,2.8,NULL,0),
(11,'/files/download/6924743913738_camera2-20.jpg','濂囧缇庡紡鐏浮鍛?0g',NULL,2.8,NULL,0),
(12,'/files/download/6909409012802_camera2-20.jpg','涓婂ソ浣崇矡绫虫潯鑽夎帗鍛?0g',NULL,4.3,NULL,0),
(13,'/files/download/6940188803618_camera2-20.jpg','鐢樻簮锜归粍鍛崇摐瀛愪粊75g',NULL,3.76,NULL,0),
(14,'/files/download/6907777825963_camera2-20.jpg',' 鎯犲疁寮€蹇冩灉140g',NULL,16.72,NULL,0),
(15,'/files/download/6907777800519_camera2-20.jpg','鎯犲疁鍜稿懗鑺辩敓350g',NULL,8.6,NULL,0),
(16,'/files/download/6907777821811_camera2-20.jpg','鎯犲疁鑵版灉160g',NULL,21.4,NULL,4),
(17,'/files/download/6907777830523_camera2-20.jpg','鎯犲疁鏋告潪100g',NULL,9.5,NULL,3),
(18,'/files/download/6907777819061_camera2-20.jpg','鎯犲疁鍦扮摐骞?28g',NULL,13.5,NULL,0),
(19,'/files/download/6907777821903_camera2-20.jpg','鎯犲疁娉板浗鑺掓灉骞?0g',NULL,5.7,NULL,0),
(20,'/files/download/6907777834712_camera2-21.jpg','鎯犲疁榛勬鏋滃共75g',NULL,5.9,NULL,0),
(21,'/files/download/6907777834705_camera2-20.jpg','鎯犲疁鏌犳鐗?5g',NULL,6.4,NULL,3),
(22,'/files/download/6940737300148_camera2-20.jpg','鏂扮枂鍜岀敯婊╂灒454g',NULL,6,NULL,2),
(23,'/files/download/6907777831995_camera2-20.jpg','鎯犲疁棣欒弴100g',NULL,6.4,NULL,0),
(24,'/files/download/6907777800151_camera2-20.jpg','鎯犲疁妗傚渾骞?00g',NULL,12,NULL,0),
(25,'/files/download/6907777808584_camera2-20.jpg','鎯犲疁鑼舵爲鑿?00g',NULL,27.4,NULL,10),
(26,'/files/download/6934848931155_camera2-20.jpg','璞泟鍗曠墖榛戞湪鑰?50g',NULL,19.9,NULL,1),
(27,'/files/download/6907777825468_camera2-20.jpg','鎯犲疁鐓姳鐢?54g',NULL,14.9,NULL,0),
(28,'/files/download/6907777815186_camera2-20.jpg','鎯犲疁榛勮姳鑿?00g',NULL,9.2,NULL,1),
(29,'/files/download/6924187829428_camera2-21.jpg','娲芥唇鍑夎尪鐡滃瓙150g',NULL,6.7,NULL,10),
(30,'/files/download/6924187828964_camera2-21.jpg','娲芥唇濂堕鍛崇摐瀛?50g',NULL,5.5,NULL,0),
(31,'/files/download/6913221220161_camera2-21.jpg','杞︿粩鑼跺寘缁胯尪50g',NULL,12.25,NULL,6),
(32,'/files/download/6913221220109_camera2-20.jpg','杞︿粩鑼跺寘绾㈣尪50g',NULL,13.2,NULL,1),
(33,'/files/download/6926475203170_camera0-31.jpg','浼樹箰缇庨鑺嬪懗80g',NULL,2.7,NULL,0),
(34,'/files/download/6926475206263_camera0-31.jpg','浼樹箰缇庣孩璞嗗ザ鑼?5g',NULL,5,NULL,0),
(35,'/files/download/6959619480205_camera0-31.jpg','娆㈡偿鍐茶皟鍦熻眴绮?5g',NULL,5.6,NULL,0),
(36,'/files/download/6939947700169_camera0-31.jpg','姹熶腑鐚村鏃╅绫崇█40g',NULL,5,NULL,0),
(37,'/files/download/6950361040808_camera2-20.jpg','姘稿拰璞嗘祮鐢滆眴娴嗙矇210g',NULL,7.62,NULL,2),
(38,'/files/download/6922848642133_camera0-31.jpg','绔嬮】鏌犳椋庡懗鑼?80g',NULL,12.78,NULL,0),
(39,'/files/download/6924743921436_camera2-21.jpg','妗傛牸澶氱鑾撴灉楹︾墖40g',NULL,2,NULL,1),
(40,'/files/download/6953787800124_camera2-20.jpg','鑽ｆ€¤胺楹﹀姞榛戠背鍛?0g',NULL,2.9,NULL,0),
(41,'/files/download/6953787800117_camera2-20.jpg','鑽ｆ€¤胺楹﹀姞绾㈣眴鍛?0g',NULL,2.9,NULL,0),
(42,'/files/download/6921555581674_camera2-20.jpg','澶т粖閲庨杈ｇ墰鑲夐潰112g',NULL,2.5,NULL,0),
(43,'/files/download/6921555510568_camera2-21.jpg','澶т粖閲庤€佸潧閰歌彍鐗涜倝闈?18g',NULL,2.5,NULL,0),
(44,'/files/download/6921555581667_camera2-20.jpg','澶т粖閲庣孩鐑х墰鑲夐潰114g',NULL,2.5,NULL,0),
(45,'/files/download/6917536014026_camera0-18.jpg','鍚堝懗閬撴捣椴滈鍛?4g',NULL,6,NULL,0),
(46,'/files/download/6920152493915_camera0-35.jpg','搴峰笀鍌呯櫧鑳℃鑲夐闈?6g',NULL,5,NULL,0),
(47,'/files/download/6920152400975_camera0-35.jpg','搴峰笀鍌呴杈ｇ墰鑲夐潰105g',NULL,4,NULL,0),
(48,'/files/download/6920152496176_camera0-31.jpg','搴峰笀鍌呰懕棣欐帓楠ㄩ潰108g',NULL,4.5,NULL,0),
(49,'/files/download/6920152497029_camera0-31.jpg','搴峰笀鍌呰棨妞掔墰鑲夐潰85g',NULL,4.5,NULL,12),
(50,'/files/download/6901715291209_camera1-20.jpg','鍗庝赴楦¤倝涓夐矞浼婇潰87g',NULL,2,NULL,1),
(51,'/files/download/6920152485095_camera2-20.jpg','搴峰笀鍌呴粦鑳℃鐗涙帓闈?04g',NULL,3,NULL,0),
(52,'/files/download/6936986841044_camera2-10.jpg','浜旇胺閬撳満绾㈢儳鐗涜倝闈?00g',NULL,2.5,NULL,0),
(53,'/files/download/6920152439005_camera2-10.jpg','搴峰笀鍌呰€佸潧閰歌彍鐗涜倝闈?14g',NULL,2.5,NULL,0),
(55,'/files/download/4894375013507_camera1-30.jpg','Aji娉¤姍楗煎共鑺掓灉鑿犺悵鍛?0g',NULL,6.4,NULL,6),
(56,'/files/download/6922907011535_camera1-30.jpg','搴嗚仈钃濊帗鍛冲す蹇冮ゼ63g',NULL,5.8,NULL,0),
(57,'/files/download/6922907011528_camera1-30.jpg','搴嗚仈鍑ゆⅷ鍛冲す蹇冮ゼ63g',NULL,5.8,NULL,3),
(58,'/files/download/6922907011511_camera1-31.jpg','搴嗚仈鑽夎帗鍛冲す蹇冮ゼ63g',NULL,5.8,NULL,0),
(59,'/files/download/6902227014843_camera1-40.jpg','鍢夐】濞佸寲楗煎共鑽夎帗鍛?0g',NULL,2,NULL,0),
(60,'/files/download/6902227014843_camera1-40.jpg','鍢夐】濞佸寲楗煎共鏌犳鍛?0g',NULL,2,NULL,12),
(61,'/files/download/6953042700220_camera1-31.jpg','鐖辨椂涔愰鑽夌墰濂跺懗50g',NULL,5,NULL,0),
(62,'/files/download/6953042700206_camera1-31.jpg','鐖辨椂涔愬阀鍏嬪姏鍛?0g',NULL,5,NULL,0),
(63,'/files/download/6901845042993_camera1-31.jpg','鐧惧姏婊嬫捣鑻斿懗60g',NULL,4.2,NULL,8),
(64,'/files/download/6901845042627_camera1-31.jpg','鐧惧姏婊嬭崏鑾撶墰濂跺懗45g',NULL,4.2,NULL,0),
(65,'/files/download/6917878035284_camera1-31.jpg','闆€宸㈣剢鑴嗛波80g',NULL,12,NULL,0),
(66,'/files/download/8993175540629_camera1-40.jpg','绾冲疂甯濆阀鍏嬪姏鍛冲▉鍖?8g',NULL,1.8,NULL,0),
(67,'/files/download/8411145202563_camera1-20.jpg','妗傚姏鍦颁腑娴烽鍛抽潰鍖呮潯50g',NULL,2.5,NULL,0),
(68,'/files/download/6920731700205_camera1-1.jpg','搴峰笀鍌呭鑺欏阀鍏嬪姏鍛?8g',NULL,4.5,NULL,0),
(69,'/files/download/6956367187172_camera1-31.jpg','鐖变埂浜插敱鐗囬潰鍖?0g',NULL,3.5,NULL,10),
(70,'/files/download/6911988005397_camera1-20.jpg','杈惧埄鍥淳鑽夎帗鍛冲崟涓',NULL,1.5,NULL,0),
(71,'/files/download/6901668054715_camera0-20.jpg','mini濂ュ埄濂?5g',NULL,6.3,NULL,3),
(72,'/files/download/6921168509256_camera0-13.jpg','鍐滃か灞辨硥鐭挎硥姘?50ml',NULL,2,NULL,0),
(73,'/files/download/6901285991219_camera0-9.jpg','鎬″疂鐭挎硥姘?55ml',NULL,2,NULL,0),
(74,'/files/download/6928804010114_camera0-30.jpg','鍙彛鍙箰闆跺害500ml',NULL,3,NULL,0),
(75,'/files/download/6928804011173_camera0-27.jpg','鍙彛鍙箰500ml',NULL,3,NULL,0),
(76,'/files/download/6924882496116_camera0-35.jpg','鐧句簨鍙箰600ml',NULL,3,NULL,2),
(77,'/files/download/6928804011456_camera0-36.jpg','鑺揪鑻规灉鍛?00ml',NULL,3,NULL,0),
(78,'/files/download/6928804011326_camera0-35.jpg','鑺揪姗欏懗500ml',NULL,3,NULL,0),
(79,'/files/download/6928804010220_camera0-35.jpg','闆ⅶ500ml',NULL,3,NULL,0),
(80,'/files/download/6953029710112_camera0-35.jpg','鍠滃姏鍟ら厭500ml',NULL,6.9,NULL,11),
(81,'/files/download/6948960100009_camera0-36.jpg','鐧惧▉鍟ら厭600ml',NULL,6,NULL,5),
(82,'/files/download/6924882486100_camera0-21.jpg','鐧句簨鍙箰330ml',NULL,2.5,NULL,0),
(83,'/files/download/6928804011142_camera0-36.jpg','鍙彛鍙箰330ml',NULL,2.5,NULL,0),
(84,'/files/download/6956367338680_camera0-34.jpg','鐜嬭€佸悏310ml',NULL,2.5,NULL,0),
(85,'/files/download/6921168593576_camera0-2.jpg','鑼舵淳鏌氬瓙缁胯尪500ml',NULL,5,NULL,0),
(86,'/files/download/6921168593736_camera0-21.jpg','鑼舵淳鐜懓鑽旀灊绾㈣尪500ml',NULL,5,NULL,7),
(87,'/files/download/6920459902387_camera0-12.jpg','搴峰笀鍌呭啺绾㈣尪250ml',NULL,1.5,NULL,0),
(88,'/files/download/4891599601138_camera0-13.jpg','鍔犲瀹?50ml',NULL,1.5,NULL,0),
(89,'/files/download/6935145301030_camera0-39.jpg','RIO鏋滈厭姘磋湝妗冨懗275ml',NULL,12,NULL,9),
(90,'/files/download/6935145301047_camera0-32.jpg','RIO鏋滈厭钃濈帿鐟板▉澹繉鍛?75ml',NULL,12,NULL,0),
(91,'/files/download/6906151601353_camera0-32.jpg','鐗涙爮灞变簩閿呭ご100ml',NULL,4.5,NULL,0),
(92,'/files/download/6948960100429_camera0-11.jpg','鍝堝皵婊ㄥ暏閰?30m',NULL,2.5,NULL,0),
(93,'/files/download/6901035613699_camera0-26.jpg','闈掑矝鍟ら厭330ml',NULL,3.5,NULL,0),
(94,'/files/download/6949352201106_camera0-31.jpg','闆姳鍟ら厭330ml',NULL,3,NULL,0),
(95,'/files/download/6948960100993_camera0-31.jpg','鍝堝皵婊ㄥ暏閰?00ml',NULL,5.5,NULL,6),
(96,'/files/download/8410793186126_camera0-31.jpg','KELER鍟ら厭500ml',NULL,6,NULL,0),
(97,'/files/download/6948960100078_camera0-31.jpg','鐧惧▉鍟ら厭500ml',NULL,6,NULL,0),
(98,'/files/download/6907992510446_camera0-33.jpg','QQ鏄熷叏鑱ザ125ml',NULL,3,NULL,2),
(99,'/files/download/6907992511559_camera0-31.jpg','QQ鏄熷潎鑶冲ザ125ml',NULL,3,NULL,1),
(100,'/files/download/6902083881085_camera0-31.jpg','濞冨搱鍝圓D閽欏ザ220g',NULL,2,NULL,0),
(101,'/files/download/6959791800068_camera0-31.jpg','娲诲姏瀹濆姩鍔涙簮105ml',NULL,2.5,NULL,3),
(102,'/files/download/6931958014105_camera0-11.jpg','鏃轰粩鐗涘ザ澶嶅師涔?50ml',NULL,2,NULL,0),
(103,'/files/download/6907992100272_camera0-31.jpg','浼婂埄绾墰濂?50ml',NULL,2,NULL,0),
(105,'/files/download/4891028707851_camera0-31.jpg','缁翠粬浣庣硸鍘熷懗璞嗗ザ250ml',NULL,2.5,NULL,0),
(106,'/files/download/6941543400251_camera0-31.jpg','鐧炬€¤姳鐢熺墰濂?50ml',NULL,2.5,NULL,0),
(107,'/files/download/6907777822948_camera0-31.jpg','鎯犲疁鍘熷懗璞嗗ザ250ml',NULL,2.5,NULL,1),
(108,'/files/download/6907992500010_camera0-31.jpg','浼婂埄浼橀吀涔?50ml',NULL,1.5,NULL,2),
(109,'/files/download/6907992504476_camera0-31.jpg','浼婂埄鏃╅濂?50ml',NULL,2.7,NULL,3),
(110,'/files/download/6911988011985_camera0-31.jpg','杈惧埄鍥鍦嗚幉瀛?60g',NULL,3.5,NULL,0),
(111,'/files/download/6926892562096_camera0-31.jpg','閾堕弓鍐扮硸鐧惧悎閾惰€?80g',NULL,4,NULL,0),
(112,'/files/download/6923523998019_camera0-31.jpg','鍠滃澶氫粈閿︽ぐ鏋?67g',NULL,2.8,NULL,6),
(113,'/files/download/4800009004827_camera0-31.jpg','閮戒箰鑿犺悵鍧?67g',NULL,19.9,NULL,1),
(114,'/files/download/038900004095_camera0-31.jpg','閮戒箰鑿犺悵鍧?34g',NULL,9.9,NULL,0),
(115,'/files/download/6926892567084_camera0-31.jpg','閾堕弓钖忎粊绾㈣眴绮?80g',NULL,3.5,NULL,0),
(116,'/files/download/6926892565080_camera0-14.jpg','閾堕弓鑾插瓙鐜夌背绮?80g',NULL,3.5,NULL,1),
(117,'/files/download/6926892501033_camera0-14.jpg','閾堕弓绱柉绱背绮?80g',NULL,3.5,NULL,0),
(118,'/files/download/6926892568081_camera0-31.jpg','閾堕弓妞板ザ鐕曢害绮?80g',NULL,3.5,NULL,4),
(119,'/files/download/6926892562003_camera0-31.jpg','閾堕弓榛戠硸妗傚渾280g',NULL,3.5,NULL,0),
(120,'/files/download/6902131110167_camera0-31.jpg','姊呮灄鍗堥鑲?40g',NULL,12.9,NULL,0),
(121,'/files/download/6916880292012_camera0-13.jpg','鐝犳睙妗ョ墝璞嗚眽楸?50g',NULL,8.9,NULL,0),
(122,'/files/download/6901073808347_camera0-13.jpg','鍙ら緳鍘熷懗榛勮姳楸?20g',NULL,7.9,NULL,0),
(123,'/files/download/9556041603720_camera0-11.jpg','闆勯浮鏍囨ぐ娴?40ml',NULL,6.5,NULL,0),
(124,'/files/download/6914973608351_camera1-31.jpg','寰疯姍鑺掓灉閰稿ザ宸у厠鍔?2g',NULL,6.5,NULL,0),
(125,'/files/download/6914973604056_camera1-31.jpg','寰疯姍鎽╁崱宸存棪鏈ㄥ阀鍏嬪姏43g',NULL,6.5,NULL,0),
(126,'/files/download/6914973608306~A_camera2-19.jpg','寰疯姍鐧鹃鏋滅櫧宸у厠鍔?2g',NULL,6.5,NULL,0),
(127,'/files/download/6914973105379_camera1-30.jpg','MM鑺辩敓鐗涘ザ宸у厠鍔涜眴40g',NULL,2.8,NULL,1),
(128,'/files/download/6914973105379_camera1-30.jpg','MM鐗涘ザ宸у厠鍔涜眴40g',NULL,2.8,NULL,0),
(129,'/files/download/6942836705916_camera1-30.jpg','濂芥椂鐗涘ザ宸у厠鍔?0g',NULL,6.6,NULL,7),
(130,'/files/download/6942836705435_camera1-31.jpg','濂芥椂鏇插濂堕鐧藉阀鍏嬪姏40g',NULL,6.6,NULL,0),
(131,'/files/download/6914973607101_camera1-30.jpg','鑴嗛绫虫捣鑻旂櫧宸у厠鍔?4g',NULL,1.8,NULL,1),
(132,'/files/download/6914973604469_camera1-29.jpg','鑴嗛绫冲ザ棣欑櫧宸у厠鍔?4g',NULL,1.8,NULL,5),
(133,'/files/download/6914973603394_camera1-31.jpg','澹姏鏋惰姳鐢熷す蹇冨阀鍏嬪姏51g',NULL,3.3,NULL,9),
(134,'/files/download/6914973607125_camera1-30.jpg','澹姏鏋剁嚂楹﹁姳鐢熷す蹇冨阀鍏嬪姏40g',NULL,3.3,NULL,1),
(135,'/files/download/6914973607637_camera1-31.jpg','澹姏鏋惰荆鑺辩敓澶瑰績宸у厠鍔?0g',NULL,3.5,NULL,0),
(136,'/files/download/6924513908216_camera0-30.jpg','鐐繄鏋滃懗娴杽鑽峰懗37g',NULL,9.9,NULL,0),
(137,'/files/download/6924513908155_camera0-30.jpg','鐐繄鏋滃懗娴煚妾懗37g',NULL,9.9,NULL,0),
(138,'/files/download/6954432710218_camera1-30.jpg','鐐繄钖勮嵎鍛?1g',NULL,4.7,NULL,0),
(139,'/files/download/6954432710621_camera1-30.jpg','鐐繄钁¤悇鍛?1g',NULL,4.7,NULL,0),
(140,'/files/download/6954432710249_camera1-31.jpg','鐐繄瑗跨摐鍛?1g',NULL,4.7,NULL,0),
(141,'/files/download/6954432710645_camera1-30.jpg','鐐繄钁¤悇鍛?0g',NULL,9.9,NULL,1),
(142,'/files/download/6923450605981_camera1-30.jpg','缁跨鏃犵硸钖勮嵎绯栬寜鑾夎姳鑼跺懗34g',NULL,10.9,NULL,0),
(143,'/files/download/69019388_camera1-30.jpg','缁跨5鐗囪15g',NULL,1.5,NULL,0),
(144,'/files/download/6911316101043_camera1-31.jpg','姣斿反鍗滄鑺辨场娉＄硸鍙箰鍛?1g',NULL,1.5,NULL,0),
(145,'/files/download/6911316101012_camera1-30.jpg','姣斿反鍗滄鑺辨场娉＄硸钁¤悇鍛?1g',NULL,1.5,NULL,0),
(146,'/files/download/6923450663981_camera0-30.jpg','鏄熺垎缂ょ悍鍘熸灉鍛?5g',NULL,3.3,NULL,0),
(147,'/files/download/6911316510005_camera1-31.jpg','闃垮皵鍗戞柉鐒﹂鐗涘ザ鍛崇‖绯?5g',NULL,2.5,NULL,5),
(148,'/files/download/6911316380288_camera1-30.jpg','闃垮皵鍗戞柉鐗涘ザ杞硸榛勬閰稿ザ鍛?7g',NULL,2.5,NULL,0),
(149,'/files/download/6911316380271_camera1-30.jpg','闃垮皵鍗戞柉鐗涘ザ杞硸钃濊帗閰稿ザ鍛?7g',NULL,2.5,NULL,0),
(150,'/files/download/6901424286213_camera1-30.jpg','鐜嬭€佸悏娑﹀枆绯?8g',NULL,3,NULL,0),
(151,'/files/download/6907992632483_camera1-29.jpg','浼婂埄鐗涘ザ鐗囪摑鑾撳懗32g',NULL,2.2,NULL,0),
(152,'/files/download/6914782114371_camera1-30.jpg','鐔婂崥澹彛鍤肩硸鑽夎帗鐗涘ザ鍛?2g',NULL,2.5,NULL,0),
(153,'/files/download/6923450603550_camera1-30.jpg','褰╄櫣绯栧師鏋滃懗45g',NULL,3.8,NULL,2),
(154,'/files/download/6932107253215_camera1-30.jpg','瀹濋紟澶╅奔闄堥吙绫抽唻245ml',NULL,5.6,NULL,9),
(155,'/files/download/6902007030087_camera1-31.jpg','鎭掗『棣欓唻340ml',NULL,1.8,NULL,0),
(156,'/files/download/6922130119954_camera1-31.jpg','澶お涔愰浮绮?00g',NULL,4,NULL,0),
(157,'/files/download/6913102210618_camera1-30.jpg','瀹朵箰棣欒弴楦¤尭姹ゆ枡41g',NULL,2.2,NULL,0),
(158,'/files/download/6907777820708_camera1-31.jpg','鎯犲疁杈ｆ绮?5g',NULL,7.5,NULL,0),
(159,'/files/download/6907777820722_camera1-31.jpg',' 鎯犲疁鐢熷绮?5g',NULL,7.6,NULL,0),
(160,'/files/download/6901844710114_camera1-31.jpg','鍛冲ソ缇庢鐩?0g',NULL,2.2,NULL,2),
(161,'/files/download/6920181360936_camera1-30.jpg','娴锋槦鍔犵绮惧埗鐩?00g',NULL,3.2,NULL,0),
(162,'/files/download/6930096350922_camera0-34.jpg','鎭掗『鏂欓厭500ml',NULL,7,NULL,0),
(163,'/files/download/6911567886393_camera0-30.jpg','涓滃彜鍛虫瀬椴滈叡娌?50ml',NULL,4.5,NULL,0),
(165,'/files/download/6911567881060_camera0-31.jpg','涓滃彜涓€鍝侀矞閰辨补150ml',NULL,4,NULL,0),
(166,'/files/download/6925843403303_camera0-31.jpg','娆ｅ拰鍏湀椴滈叡娌?60ml',NULL,5.2,NULL,0),
(167,'/files/download/6907376820598_camera0-31.jpg','鏉庢柦寰锋灄闆跺害婕卞彛姘?0ml',NULL,5,NULL,0),
(168,'/files/download/6903148232965_camera0-31.jpg','鑸掕偆浣崇函鐧芥竻棣欐矏娴撮湶100ml',NULL,6.6,NULL,0),
(169,'/files/download/6924882349016_camera0-31.jpg','缇庢稕瀹氬瀷鍟柋姘?0ml',NULL,6,NULL,0),
(170,'/files/download/6902088119435_camera0-31.jpg','娓呮壃鐢峰＋娲楀彂闇叉椿鍔涜繍鍔ㄨ杽鑽峰瀷50ml',NULL,4.5,NULL,0),
(171,'/files/download/6902022138102_camera0-31.jpg','钃濇湀浜娓呯櫧鍏版礂琛ｆ恫80g',NULL,6.5,NULL,0),
(172,'/files/download/6920354818585_camera1-20.jpg','楂橀湶娲佷寒鐧藉皬鑻忔墦180g',NULL,12.9,NULL,0),
(173,'/files/download/6920354808388_camera1-20.jpg','楂橀湶娲佸啺鐖?80g',NULL,13.9,NULL,3),
(174,'/files/download/6921469850194_camera1-20.jpg','鑸掍寒鐨撻娇鐧?0g',NULL,9.9,NULL,0),
(175,'/files/download/6901070600128_camera1-21.jpg','浜戝崡鐧借嵂鐗欒啅45g',NULL,9.9,NULL,0),
(176,'/files/download/6940477401396_camera1-30.jpg','鑸掑厠瀹濊礉鍎跨鐗欏埛',NULL,6.8,NULL,0),
(177,'/files/download/6922266452949_camera1-1.jpg','娓呴鍘熸湪绾搧閲戣100x3',NULL,1.8,NULL,3),
(178,'/files/download/6914068016115_camera1-20.jpg','娲佹煍face150x3',NULL,2.53,NULL,0),
(179,'/files/download/6953631801604_camera1-21.jpg','鏂戝竷100x3',NULL,2.65,NULL,9),
(180,'/files/download/6901236378823_camera1-39.jpg','缁磋揪濠村効150x3',NULL,6.1,NULL,10),
(181,'/files/download/6922868286249_camera1-40.jpg','蹇冪浉鍗板皬榛勪汉150x3',NULL,2.2,NULL,15),
(182,'/files/download/6922266457616_camera1-40.jpg','娓呴鍘熸湪绾搧榛戣€€绯诲垪100x3',NULL,3.8,NULL,0),
(183,'/files/download/6918717002160_camera1-39.jpg','娲佷簯缁掕Е鎰?00x3',NULL,1.56,NULL,0),
(184,'/files/download/6923589421131_camera1-39.jpg','鑸掓磥鑷虫煍鍗囩骇100x3',NULL,2.9,NULL,3),
(185,'/files/download/6903244670166_camera1-40.jpg','蹇冪浉鍗扮孩鎮?00x3',NULL,2.5,NULL,0),
(186,'/files/download/6947509910727_camera1-39.jpg','寰楀疂100x3',NULL,4.5,NULL,0),
(187,'/files/download/6922266449611_camera1-40.jpg','娓呴鏂伴煣绾搧100x3',NULL,1.8,NULL,0),
(188,'/files/download/6951481302241_camera1-40.jpg','閲戦奔100x3',NULL,1.85,NULL,0),
(189,'/files/download/6922266444463_camera1-40.jpg','娓呴鍘熸湪绾搧100x3',NULL,1.6,NULL,0),
(190,'/files/download/6914068018171_camera1-40.jpg','娲佹煍鍙箍姘撮潰绾稿姞鍘?00x3',NULL,2.7,NULL,4),
(191,'/files/download/6901236344033_camera1-23.jpg','缁磋揪绔嬩綋缇?00x3',NULL,2.5,NULL,3),
(192,'/files/download/6914068016535_camera1-31.jpg','娲佹煍鎵嬪笗绾?,NULL,1,NULL,0),
(193,'/files/download/6922868282265_camera1-31.jpg','蹇冪浉鍗板皬榛勪汉鎵嬪笗绾?,NULL,1,NULL,0),
(194,'/files/download/6922266457425_camera1-31.jpg','鍘熻壊绾告墜甯曠焊',NULL,1,NULL,0),
(195,'/files/download/6922868290932_camera1-31.jpg','蹇冪浉鍗拌尪璇墜甯曠焊',NULL,1,NULL,0),
(196,'/files/download/6922266426001_camera1-31.jpg','娓呴璐ㄦ劅绾搧鎵嬪笗绾?,NULL,1,NULL,0),
(197,'/files/download/6901687353417_camera1-30.jpg','杩＋灏肩瑪璁扮翱',NULL,3.5,NULL,0),
(198,'/files/download/6930114504085_camera0-18.jpg','涓夎鍥轰綋妫?,NULL,2.5,NULL,2),
(199,'/files/download/6951384903194_camera1-40.jpg','钃濊壊绗旇',NULL,5.5,NULL,0),
(200,'/files/download/6933631504811_camera1-31.jpg','鏅ㄥ厜鎷煎惂灏忚湕鐗涗慨姝ｅ甫',NULL,3.5,NULL,0),
(201,'/files/download/6933093050208_camera0-22.jpg','TAIPAI娑蹭綋鑳?,NULL,2.5,NULL,0),
(202,'/files/download/6939789303252_camera1-30.jpg','椹煿寰疯嚜绮樻爣绛?,NULL,2.5,NULL,0),
(203,'/files/download/6925792550042_camera0-20.jpg','涓滀簹璁板彿绗?,NULL,2.6,NULL,0);

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '璐﹀彿',
  `password` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '瀵嗙爜',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '鐢ㄦ埛鍚?,
  `email` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '閭',
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '鐢佃瘽鍙风爜',
  `sex` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '鎬у埆',
  `avatar` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '澶村儚',
  `role` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '瑙掕壊',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='鐢ㄦ埛淇℃伅';

/*Data for the table `user` */

insert  into `user`(`id`,`username`,`password`,`name`,`email`,`phone`,`sex`,`avatar`,`role`) values
(1,'1','1','1',NULL,'19565999949','鐢?,'/files/download/榛樿澶村儚.jpg','鏅€氱敤鎴?),
(5,'3','3','3',NULL,'123','濂?,'/files/download/榛樿澶村儚.jpg','鏅€氱敤鎴?),
(10,'2','2','2',NULL,'18455940682',NULL,'/files/download/榛樿澶村儚.jpg','鏅€氱敤鎴?);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
