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
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '账号',
  `password` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '密码',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户名',
  `avatar` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像',
  `role` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '角色',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='管理员信息';

/*Data for the table `admin` */

insert  into `admin`(`id`,`username`,`password`,`name`,`avatar`,`role`) values 
(1,'飞起','1','超级管理员','http://localhost:9090/files/download/默认管理员头像.jpg','管理员');

/*Table structure for table `feedback` */

DROP TABLE IF EXISTS `feedback`;

CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '反馈id',
  `userId` int DEFAULT NULL COMMENT '用户id',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '用户名称',
  `content` varchar(1000) DEFAULT NULL COMMENT '反馈内容',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '反馈时间',
  `status` tinyint DEFAULT '0' COMMENT '状态：0-未读，1-已读',
  `reply` varchar(1000) DEFAULT NULL COMMENT '管理员回复',
  `reply_time` datetime DEFAULT NULL COMMENT '回复时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`userId`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户反馈表';

/*Data for the table `feedback` */

/*Table structure for table `pricing_record` */

DROP TABLE IF EXISTS `pricing_record`;

CREATE TABLE `pricing_record` (
  `id` varchar(64) NOT NULL COMMENT '记录ID',
  `image_path` varchar(255) NOT NULL COMMENT '检测图片路径',
  `total_price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '总价格',
  `item_count` int NOT NULL DEFAULT '0' COMMENT '商品总数量',
  `detection_duration` float NOT NULL COMMENT '检测用时(ms)',
  `execute_duration` float NOT NULL COMMENT '执行时长(s)',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `create_user_id` varchar(64) DEFAULT NULL COMMENT '创建用户ID',
  `create_user_name` varchar(100) DEFAULT NULL COMMENT '创建用户名称',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='计价记录表';

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
  `id` varchar(64) NOT NULL COMMENT '项目ID',
  `record_id` varchar(64) NOT NULL COMMENT '关联的记录ID',
  `name` varchar(100) NOT NULL COMMENT '商品名称',
  `count` int NOT NULL DEFAULT '1' COMMENT '商品数量',
  `price` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '商品单价',
  PRIMARY KEY (`id`),
  KEY `idx_record_id` (`record_id`),
  CONSTRAINT `pricing_record_item_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `pricing_record` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `pricing_record_item` */

insert  into `pricing_record_item`(`id`,`record_id`,`name`,`count`,`price`) values 
('01cfe134b78e4e0db821019354890fae','3c86cdf35c984b95b46e883c248483db','嘉顿威化饼干柠檬味50g',3,2.00),
('0c0541113ece486db67c907cb8914d62','3c86cdf35c984b95b46e883c248483db','银鹭椰奶燕麦粥280g',1,3.50),
('1af586a352e74b8294aace3573fc8073','969c16f6d381450cb7cb583baa84f638','喜力啤酒500ml',1,6.90),
('2c6358c8611946a5a4ec9e0d86b74862','969c16f6d381450cb7cb583baa84f638','维达婴儿150x3',1,6.10),
('393e2baaa0fd4646a419bb1ad43556c4','4a2f8ddee5e341069aa2550124e4b888','惠宜腰果160g',1,21.40),
('3d6aad10208c4e6a918eed44455dee8c','969c16f6d381450cb7cb583baa84f638','菜园小饼80g',3,1.60),
('3e106ba274a7459dbe2ff25c323b4b1f','d5e2e40286734423869ea226682ddde5','心相印小黄人150x3',3,2.20),
('42e264b32b8b466bbbed6cff9421c2ad','69bdf4cf9def4d81b921d31b54b9a912','QQ星均膳奶125ml',1,3.00),
('4cee793a1ff84ad3abc501e3b5170239','69bdf4cf9def4d81b921d31b54b9a912','阿尔卑斯焦香牛奶味硬糖45g',2,2.50),
('52cdcf0cc3d94d37920e4a80f4175779','969c16f6d381450cb7cb583baa84f638','百威啤酒600ml',2,6.00),
('55f9863432914d889f00213eef79cc2f','8779df7728ad4c229dd8e374ccbe0bf1','妙脆角魔力炭烧味65g',1,6.55),
('565d47fb4e79496292d232a88c6c9f31','69bdf4cf9def4d81b921d31b54b9a912','华丰鸡肉三鲜伊面87g',1,2.00),
('78b020727db64722bcaf63d29a3d9a27','3c86cdf35c984b95b46e883c248483db','士力架花生夹心巧克力51g',3,3.30),
('85210f2178b94194a611a8c573f7215d','58a2c534320f46d6be05e0d649858e12','洽洽凉茶瓜子150g',2,6.70),
('8e12678929e64ad689ccaf1977a5e319','4a2f8ddee5e341069aa2550124e4b888','康师傅藤椒牛肉面85g',3,4.50),
('8ee87e63de7f476980d9583a573952e7','d5e2e40286734423869ea226682ddde5','喜力啤酒500ml',2,6.90),
('929ad3b042c44fdfa596ad03ec7e611e','8779df7728ad4c229dd8e374ccbe0bf1','宝鼎天鱼陈酿米醋245ml',1,5.60),
('9641426ed23246c98c894c3fca5a1e08','69bdf4cf9def4d81b921d31b54b9a912','清风原木纯品金装100x3',3,1.80),
('9838cafc9d4a4300bfe26fa479c160b8','3c86cdf35c984b95b46e883c248483db','妙脆角魔力炭烧味65g',1,6.55),
('a07d903142b3470cb72b50e21f1882bd','69bdf4cf9def4d81b921d31b54b9a912','新疆和田滩枣454g',2,6.00),
('adced316bf134c6c86a6a2282da7765c','69bdf4cf9def4d81b921d31b54b9a912','都乐菠萝块567g',1,19.90),
('c273ec03117a47ada3c44566545b201a','3c86cdf35c984b95b46e883c248483db','宝鼎天鱼陈酿米醋245ml',2,5.60),
('c881bf2e400748e5afc46a4b8031ce57','969c16f6d381450cb7cb583baa84f638','茶派玫瑰荔枝红茶500ml',2,5.00),
('d1813e37074d4a02b74f58a41480a86b','d5e2e40286734423869ea226682ddde5','茶派玫瑰荔枝红茶500ml',1,5.00),
('d40ca890780347b6bfca7358dc679074','58a2c534320f46d6be05e0d649858e12','百力滋海苔味60g',2,4.20),
('d6d9862937074ff49a525fc723460671','58a2c534320f46d6be05e0d649858e12','斑布100x3',1,2.65),
('d8d493ab2e00494daf83f7683b560095','4a2f8ddee5e341069aa2550124e4b888','爱乡亲唱片面包90g',2,3.50),
('f7e0c07f884b406d81c2c540cef2bb5a','8779df7728ad4c229dd8e374ccbe0bf1','伊利早餐奶250ml',1,2.70),
('fcdd96c257504e5f9abb1297cd111400','8779df7728ad4c229dd8e374ccbe0bf1','百威啤酒600ml',3,6.00);

/*Table structure for table `product` */

DROP TABLE IF EXISTS `product`;

CREATE TABLE `product` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '商品主id',
  `image` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '商品图片',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '商品名称',
  `category_id` int DEFAULT NULL COMMENT '商品属类id',
  `price` double DEFAULT NULL COMMENT '商品价格',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `sales` int DEFAULT '0' COMMENT '商品销售量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `product` */

insert  into `product`(`id`,`image`,`name`,`category_id`,`price`,`remark`,`sales`) values 
(1,'http://localhost:9090/files/download/6909409012031_camera2-20.jpg','上好佳荷兰豆55g',NULL,3.5,NULL,0),
(2,'http://localhost:9090/files/download/6901845043112_camera2-19.jpg','菜园小饼80g',NULL,1.6,NULL,6),
(3,'http://localhost:9090/files/download/6909409012024_camera2-20.jpg','上好佳鲜虾片40g',NULL,3.5,NULL,0),
(4,'http://localhost:9090/files/download/6926265388100_camera2-20.jpg','上好佳蟹味逸族40g',NULL,4.2,NULL,0),
(5,'http://localhost:9090/files/download/6924743920330_camera2-20.jpg','妙脆角魔力炭烧味65g',NULL,6.55,NULL,5),
(6,'http://localhost:9090/files/download/6920912342002_camera2-20.jpg','盼盼烧烤牛排味块105g',NULL,4.8,NULL,0),
(7,'http://localhost:9090/files/download/6926265301024_camera2-20.jpg','上好佳鲜虾条40g',NULL,4.6,NULL,1),
(8,'http://localhost:9090/files/download/6909409040799_camera2-19.jpg','上好佳洋葱圈40g',NULL,5.6,NULL,3),
(9,'http://localhost:9090/files/download/6926265301130_camera2-20.jpg','上好佳日式鱼果海苔味50g',NULL,4.5,NULL,0),
(10,'http://localhost:9090/files/download/6924743913721_camera2-20.jpg','奇多日式牛排味90g',NULL,2.8,NULL,0),
(11,'http://localhost:9090/files/download/6924743913738_camera2-20.jpg','奇多美式火鸡味90g',NULL,2.8,NULL,0),
(12,'http://localhost:9090/files/download/6909409012802_camera2-20.jpg','上好佳粟米条草莓味40g',NULL,4.3,NULL,0),
(13,'http://localhost:9090/files/download/6940188803618_camera2-20.jpg','甘源蟹黄味瓜子仁75g',NULL,3.76,NULL,0),
(14,'http://localhost:9090/files/download/6907777825963_camera2-20.jpg',' 惠宜开心果140g',NULL,16.72,NULL,0),
(15,'http://localhost:9090/files/download/6907777800519_camera2-20.jpg','惠宜咸味花生350g',NULL,8.6,NULL,0),
(16,'http://localhost:9090/files/download/6907777821811_camera2-20.jpg','惠宜腰果160g',NULL,21.4,NULL,4),
(17,'http://localhost:9090/files/download/6907777830523_camera2-20.jpg','惠宜枸杞100g',NULL,9.5,NULL,3),
(18,'http://localhost:9090/files/download/6907777819061_camera2-20.jpg','惠宜地瓜干228g',NULL,13.5,NULL,0),
(19,'http://localhost:9090/files/download/6907777821903_camera2-20.jpg','惠宜泰国芒果干80g',NULL,5.7,NULL,0),
(20,'http://localhost:9090/files/download/6907777834712_camera2-21.jpg','惠宜黄桃果干75g',NULL,5.9,NULL,0),
(21,'http://localhost:9090/files/download/6907777834705_camera2-20.jpg','惠宜柠檬片65g',NULL,6.4,NULL,3),
(22,'http://localhost:9090/files/download/6940737300148_camera2-20.jpg','新疆和田滩枣454g',NULL,6,NULL,2),
(23,'http://localhost:9090/files/download/6907777831995_camera2-20.jpg','惠宜香菇100g',NULL,6.4,NULL,0),
(24,'http://localhost:9090/files/download/6907777800151_camera2-20.jpg','惠宜桂圆干500g',NULL,12,NULL,0),
(25,'http://localhost:9090/files/download/6907777808584_camera2-20.jpg','惠宜茶树菇200g',NULL,27.4,NULL,10),
(26,'http://localhost:9090/files/download/6934848931155_camera2-20.jpg','豪雄单片黑木耳150g',NULL,19.9,NULL,1),
(27,'http://localhost:9090/files/download/6907777825468_camera2-20.jpg','惠宜煮花生454g',NULL,14.9,NULL,0),
(28,'http://localhost:9090/files/download/6907777815186_camera2-20.jpg','惠宜黄花菜100g',NULL,9.2,NULL,1),
(29,'http://localhost:9090/files/download/6924187829428_camera2-21.jpg','洽洽凉茶瓜子150g',NULL,6.7,NULL,10),
(30,'http://localhost:9090/files/download/6924187828964_camera2-21.jpg','洽洽奶香味瓜子150g',NULL,5.5,NULL,0),
(31,'http://localhost:9090/files/download/6913221220161_camera2-21.jpg','车仔茶包绿茶50g',NULL,12.25,NULL,6),
(32,'http://localhost:9090/files/download/6913221220109_camera2-20.jpg','车仔茶包红茶50g',NULL,13.2,NULL,1),
(33,'http://localhost:9090/files/download/6926475203170_camera0-31.jpg','优乐美香芋味80g',NULL,2.7,NULL,0),
(34,'http://localhost:9090/files/download/6926475206263_camera0-31.jpg','优乐美红豆奶茶65g',NULL,5,NULL,0),
(35,'http://localhost:9090/files/download/6959619480205_camera0-31.jpg','欢泥冲调土豆粥25g',NULL,5.6,NULL,0),
(36,'http://localhost:9090/files/download/6939947700169_camera0-31.jpg','江中猴姑早餐米稀40g',NULL,5,NULL,0),
(37,'http://localhost:9090/files/download/6950361040808_camera2-20.jpg','永和豆浆甜豆浆粉210g',NULL,7.62,NULL,2),
(38,'http://localhost:9090/files/download/6922848642133_camera0-31.jpg','立顿柠檬风味茶180g',NULL,12.78,NULL,0),
(39,'http://localhost:9090/files/download/6924743921436_camera2-21.jpg','桂格多种莓果麦片40g',NULL,2,NULL,1),
(40,'http://localhost:9090/files/download/6953787800124_camera2-20.jpg','荣怡谷麦加黑米味30g',NULL,2.9,NULL,0),
(41,'http://localhost:9090/files/download/6953787800117_camera2-20.jpg','荣怡谷麦加红豆味30g',NULL,2.9,NULL,0),
(42,'http://localhost:9090/files/download/6921555581674_camera2-20.jpg','大今野香辣牛肉面112g',NULL,2.5,NULL,0),
(43,'http://localhost:9090/files/download/6921555510568_camera2-21.jpg','大今野老坛酸菜牛肉面118g',NULL,2.5,NULL,0),
(44,'http://localhost:9090/files/download/6921555581667_camera2-20.jpg','大今野红烧牛肉面114g',NULL,2.5,NULL,0),
(45,'http://localhost:9090/files/download/6917536014026_camera0-18.jpg','合味道海鲜风味84g',NULL,6,NULL,0),
(46,'http://localhost:9090/files/download/6920152493915_camera0-35.jpg','康师傅白胡椒肉骨面76g',NULL,5,NULL,0),
(47,'http://localhost:9090/files/download/6920152400975_camera0-35.jpg','康师傅香辣牛肉面105g',NULL,4,NULL,0),
(48,'http://localhost:9090/files/download/6920152496176_camera0-31.jpg','康师傅葱香排骨面108g',NULL,4.5,NULL,0),
(49,'http://localhost:9090/files/download/6920152497029_camera0-31.jpg','康师傅藤椒牛肉面85g',NULL,4.5,NULL,12),
(50,'http://localhost:9090/files/download/6901715291209_camera1-20.jpg','华丰鸡肉三鲜伊面87g',NULL,2,NULL,1),
(51,'http://localhost:9090/files/download/6920152485095_camera2-20.jpg','康师傅黑胡椒牛排面104g',NULL,3,NULL,0),
(52,'http://localhost:9090/files/download/6936986841044_camera2-10.jpg','五谷道场红烧牛肉面100g',NULL,2.5,NULL,0),
(53,'http://localhost:9090/files/download/6920152439005_camera2-10.jpg','康师傅老坛酸菜牛肉面114g',NULL,2.5,NULL,0),
(55,'http://localhost:9090/files/download/4894375013507_camera1-30.jpg','Aji泡芙饼干芒果菠萝味60g',NULL,6.4,NULL,6),
(56,'http://localhost:9090/files/download/6922907011535_camera1-30.jpg','庆联蓝莓味夹心饼63g',NULL,5.8,NULL,0),
(57,'http://localhost:9090/files/download/6922907011528_camera1-30.jpg','庆联凤梨味夹心饼63g',NULL,5.8,NULL,3),
(58,'http://localhost:9090/files/download/6922907011511_camera1-31.jpg','庆联草莓味夹心饼63g',NULL,5.8,NULL,0),
(59,'http://localhost:9090/files/download/6902227014843_camera1-40.jpg','嘉顿威化饼干草莓味50g',NULL,2,NULL,0),
(60,'http://localhost:9090/files/download/6902227014843_camera1-40.jpg','嘉顿威化饼干柠檬味50g',NULL,2,NULL,12),
(61,'http://localhost:9090/files/download/6953042700220_camera1-31.jpg','爱时乐香草牛奶味50g',NULL,5,NULL,0),
(62,'http://localhost:9090/files/download/6953042700206_camera1-31.jpg','爱时乐巧克力味50g',NULL,5,NULL,0),
(63,'http://localhost:9090/files/download/6901845042993_camera1-31.jpg','百力滋海苔味60g',NULL,4.2,NULL,8),
(64,'http://localhost:9090/files/download/6901845042627_camera1-31.jpg','百力滋草莓牛奶味45g',NULL,4.2,NULL,0),
(65,'http://localhost:9090/files/download/6917878035284_camera1-31.jpg','雀巢脆脆鲨80g',NULL,12,NULL,0),
(66,'http://localhost:9090/files/download/8993175540629_camera1-40.jpg','纳宝帝巧克力味威化58g',NULL,1.8,NULL,0),
(67,'http://localhost:9090/files/download/8411145202563_camera1-20.jpg','桂力地中海风味面包条50g',NULL,2.5,NULL,0),
(68,'http://localhost:9090/files/download/6920731700205_camera1-1.jpg','康师傅妙芙巧克力味48g',NULL,4.5,NULL,0),
(69,'http://localhost:9090/files/download/6956367187172_camera1-31.jpg','爱乡亲唱片面包90g',NULL,3.5,NULL,10),
(70,'http://localhost:9090/files/download/6911988005397_camera1-20.jpg','达利园派草莓味单个装',NULL,1.5,NULL,0),
(71,'http://localhost:9090/files/download/6901668054715_camera0-20.jpg','mini奥利奥55g',NULL,6.3,NULL,3),
(72,'http://localhost:9090/files/download/6921168509256_camera0-13.jpg','农夫山泉矿泉水550ml',NULL,2,NULL,0),
(73,'http://localhost:9090/files/download/6901285991219_camera0-9.jpg','怡宝矿泉水555ml',NULL,2,NULL,0),
(74,'http://localhost:9090/files/download/6928804010114_camera0-30.jpg','可口可乐零度500ml',NULL,3,NULL,0),
(75,'http://localhost:9090/files/download/6928804011173_camera0-27.jpg','可口可乐500ml',NULL,3,NULL,0),
(76,'http://localhost:9090/files/download/6924882496116_camera0-35.jpg','百事可乐600ml',NULL,3,NULL,2),
(77,'http://localhost:9090/files/download/6928804011456_camera0-36.jpg','芬达苹果味500ml',NULL,3,NULL,0),
(78,'http://localhost:9090/files/download/6928804011326_camera0-35.jpg','芬达橙味500ml',NULL,3,NULL,0),
(79,'http://localhost:9090/files/download/6928804010220_camera0-35.jpg','雪碧500ml',NULL,3,NULL,0),
(80,'http://localhost:9090/files/download/6953029710112_camera0-35.jpg','喜力啤酒500ml',NULL,6.9,NULL,11),
(81,'http://localhost:9090/files/download/6948960100009_camera0-36.jpg','百威啤酒600ml',NULL,6,NULL,5),
(82,'http://localhost:9090/files/download/6924882486100_camera0-21.jpg','百事可乐330ml',NULL,2.5,NULL,0),
(83,'http://localhost:9090/files/download/6928804011142_camera0-36.jpg','可口可乐330ml',NULL,2.5,NULL,0),
(84,'http://localhost:9090/files/download/6956367338680_camera0-34.jpg','王老吉310ml',NULL,2.5,NULL,0),
(85,'http://localhost:9090/files/download/6921168593576_camera0-2.jpg','茶派柚子绿茶500ml',NULL,5,NULL,0),
(86,'http://localhost:9090/files/download/6921168593736_camera0-21.jpg','茶派玫瑰荔枝红茶500ml',NULL,5,NULL,7),
(87,'http://localhost:9090/files/download/6920459902387_camera0-12.jpg','康师傅冰红茶250ml',NULL,1.5,NULL,0),
(88,'http://localhost:9090/files/download/4891599601138_camera0-13.jpg','加多宝250ml',NULL,1.5,NULL,0),
(89,'http://localhost:9090/files/download/6935145301030_camera0-39.jpg','RIO果酒水蜜桃味275ml',NULL,12,NULL,9),
(90,'http://localhost:9090/files/download/6935145301047_camera0-32.jpg','RIO果酒蓝玫瑰威士忌味275ml',NULL,12,NULL,0),
(91,'http://localhost:9090/files/download/6906151601353_camera0-32.jpg','牛栏山二锅头100ml',NULL,4.5,NULL,0),
(92,'http://localhost:9090/files/download/6948960100429_camera0-11.jpg','哈尔滨啤酒330m',NULL,2.5,NULL,0),
(93,'http://localhost:9090/files/download/6901035613699_camera0-26.jpg','青岛啤酒330ml',NULL,3.5,NULL,0),
(94,'http://localhost:9090/files/download/6949352201106_camera0-31.jpg','雪花啤酒330ml',NULL,3,NULL,0),
(95,'http://localhost:9090/files/download/6948960100993_camera0-31.jpg','哈尔滨啤酒500ml',NULL,5.5,NULL,6),
(96,'http://localhost:9090/files/download/8410793186126_camera0-31.jpg','KELER啤酒500ml',NULL,6,NULL,0),
(97,'http://localhost:9090/files/download/6948960100078_camera0-31.jpg','百威啤酒500ml',NULL,6,NULL,0),
(98,'http://localhost:9090/files/download/6907992510446_camera0-33.jpg','QQ星全聪奶125ml',NULL,3,NULL,2),
(99,'http://localhost:9090/files/download/6907992511559_camera0-31.jpg','QQ星均膳奶125ml',NULL,3,NULL,1),
(100,'http://localhost:9090/files/download/6902083881085_camera0-31.jpg','娃哈哈AD钙奶220g',NULL,2,NULL,0),
(101,'http://localhost:9090/files/download/6959791800068_camera0-31.jpg','活力宝动力源105ml',NULL,2.5,NULL,3),
(102,'http://localhost:9090/files/download/6931958014105_camera0-11.jpg','旺仔牛奶复原乳250ml',NULL,2,NULL,0),
(103,'http://localhost:9090/files/download/6907992100272_camera0-31.jpg','伊利纯牛奶250ml',NULL,2,NULL,0),
(105,'http://localhost:9090/files/download/4891028707851_camera0-31.jpg','维他低糖原味豆奶250ml',NULL,2.5,NULL,0),
(106,'http://localhost:9090/files/download/6941543400251_camera0-31.jpg','百怡花生牛奶250ml',NULL,2.5,NULL,0),
(107,'http://localhost:9090/files/download/6907777822948_camera0-31.jpg','惠宜原味豆奶250ml',NULL,2.5,NULL,1),
(108,'http://localhost:9090/files/download/6907992500010_camera0-31.jpg','伊利优酸乳250ml',NULL,1.5,NULL,2),
(109,'http://localhost:9090/files/download/6907992504476_camera0-31.jpg','伊利早餐奶250ml',NULL,2.7,NULL,3),
(110,'http://localhost:9090/files/download/6911988011985_camera0-31.jpg','达利园桂圆莲子360g',NULL,3.5,NULL,0),
(111,'http://localhost:9090/files/download/6926892562096_camera0-31.jpg','银鹭冰糖百合银耳280g',NULL,4,NULL,0),
(112,'http://localhost:9090/files/download/6923523998019_camera0-31.jpg','喜多多什锦椰果567g',NULL,2.8,NULL,6),
(113,'http://localhost:9090/files/download/4800009004827_camera0-31.jpg','都乐菠萝块567g',NULL,19.9,NULL,1),
(114,'http://localhost:9090/files/download/038900004095_camera0-31.jpg','都乐菠萝块234g',NULL,9.9,NULL,0),
(115,'http://localhost:9090/files/download/6926892567084_camera0-31.jpg','银鹭薏仁红豆粥280g',NULL,3.5,NULL,0),
(116,'http://localhost:9090/files/download/6926892565080_camera0-14.jpg','银鹭莲子玉米粥280g',NULL,3.5,NULL,1),
(117,'http://localhost:9090/files/download/6926892501033_camera0-14.jpg','银鹭紫薯紫米粥280g',NULL,3.5,NULL,0),
(118,'http://localhost:9090/files/download/6926892568081_camera0-31.jpg','银鹭椰奶燕麦粥280g',NULL,3.5,NULL,4),
(119,'http://localhost:9090/files/download/6926892562003_camera0-31.jpg','银鹭黑糖桂圆280g',NULL,3.5,NULL,0),
(120,'http://localhost:9090/files/download/6902131110167_camera0-31.jpg','梅林午餐肉340g',NULL,12.9,NULL,0),
(121,'http://localhost:9090/files/download/6916880292012_camera0-13.jpg','珠江桥牌豆豉鱼150g',NULL,8.9,NULL,0),
(122,'http://localhost:9090/files/download/6901073808347_camera0-13.jpg','古龙原味黄花鱼120g',NULL,7.9,NULL,0),
(123,'http://localhost:9090/files/download/9556041603720_camera0-11.jpg','雄鸡标椰浆140ml',NULL,6.5,NULL,0),
(124,'http://localhost:9090/files/download/6914973608351_camera1-31.jpg','德芙芒果酸奶巧克力42g',NULL,6.5,NULL,0),
(125,'http://localhost:9090/files/download/6914973604056_camera1-31.jpg','德芙摩卡巴旦木巧克力43g',NULL,6.5,NULL,0),
(126,'http://localhost:9090/files/download/6914973608306~A_camera2-19.jpg','德芙百香果白巧克力42g',NULL,6.5,NULL,0),
(127,'http://localhost:9090/files/download/6914973105379_camera1-30.jpg','MM花生牛奶巧克力豆40g',NULL,2.8,NULL,1),
(128,'http://localhost:9090/files/download/6914973105379_camera1-30.jpg','MM牛奶巧克力豆40g',NULL,2.8,NULL,0),
(129,'http://localhost:9090/files/download/6942836705916_camera1-30.jpg','好时牛奶巧克力40g',NULL,6.6,NULL,7),
(130,'http://localhost:9090/files/download/6942836705435_camera1-31.jpg','好时曲奇奶香白巧克力40g',NULL,6.6,NULL,0),
(131,'http://localhost:9090/files/download/6914973607101_camera1-30.jpg','脆香米海苔白巧克力24g',NULL,1.8,NULL,1),
(132,'http://localhost:9090/files/download/6914973604469_camera1-29.jpg','脆香米奶香白巧克力24g',NULL,1.8,NULL,5),
(133,'http://localhost:9090/files/download/6914973603394_camera1-31.jpg','士力架花生夹心巧克力51g',NULL,3.3,NULL,9),
(134,'http://localhost:9090/files/download/6914973607125_camera1-30.jpg','士力架燕麦花生夹心巧克力40g',NULL,3.3,NULL,1),
(135,'http://localhost:9090/files/download/6914973607637_camera1-31.jpg','士力架辣花生夹心巧克力40g',NULL,3.5,NULL,0),
(136,'http://localhost:9090/files/download/6924513908216_camera0-30.jpg','炫迈果味浪薄荷味37g',NULL,9.9,NULL,0),
(137,'http://localhost:9090/files/download/6924513908155_camera0-30.jpg','炫迈果味浪柠檬味37g',NULL,9.9,NULL,0),
(138,'http://localhost:9090/files/download/6954432710218_camera1-30.jpg','炫迈薄荷味21g',NULL,4.7,NULL,0),
(139,'http://localhost:9090/files/download/6954432710621_camera1-30.jpg','炫迈葡萄味21g',NULL,4.7,NULL,0),
(140,'http://localhost:9090/files/download/6954432710249_camera1-31.jpg','炫迈西瓜味21g',NULL,4.7,NULL,0),
(141,'http://localhost:9090/files/download/6954432710645_camera1-30.jpg','炫迈葡萄味50g',NULL,9.9,NULL,1),
(142,'http://localhost:9090/files/download/6923450605981_camera1-30.jpg','绿箭无糖薄荷糖茉莉花茶味34g',NULL,10.9,NULL,0),
(143,'http://localhost:9090/files/download/69019388_camera1-30.jpg','绿箭5片装15g',NULL,1.5,NULL,0),
(144,'http://localhost:9090/files/download/6911316101043_camera1-31.jpg','比巴卜棉花泡泡糖可乐味11g',NULL,1.5,NULL,0),
(145,'http://localhost:9090/files/download/6911316101012_camera1-30.jpg','比巴卜棉花泡泡糖葡萄味11g',NULL,1.5,NULL,0),
(146,'http://localhost:9090/files/download/6923450663981_camera0-30.jpg','星爆缤纷原果味25g',NULL,3.3,NULL,0),
(147,'http://localhost:9090/files/download/6911316510005_camera1-31.jpg','阿尔卑斯焦香牛奶味硬糖45g',NULL,2.5,NULL,5),
(148,'http://localhost:9090/files/download/6911316380288_camera1-30.jpg','阿尔卑斯牛奶软糖黄桃酸奶味47g',NULL,2.5,NULL,0),
(149,'http://localhost:9090/files/download/6911316380271_camera1-30.jpg','阿尔卑斯牛奶软糖蓝莓酸奶味47g',NULL,2.5,NULL,0),
(150,'http://localhost:9090/files/download/6901424286213_camera1-30.jpg','王老吉润喉糖28g',NULL,3,NULL,0),
(151,'http://localhost:9090/files/download/6907992632483_camera1-29.jpg','伊利牛奶片蓝莓味32g',NULL,2.2,NULL,0),
(152,'http://localhost:9090/files/download/6914782114371_camera1-30.jpg','熊博士口嚼糖草莓牛奶味52g',NULL,2.5,NULL,0),
(153,'http://localhost:9090/files/download/6923450603550_camera1-30.jpg','彩虹糖原果味45g',NULL,3.8,NULL,2),
(154,'http://localhost:9090/files/download/6932107253215_camera1-30.jpg','宝鼎天鱼陈酿米醋245ml',NULL,5.6,NULL,9),
(155,'http://localhost:9090/files/download/6902007030087_camera1-31.jpg','恒顺香醋340ml',NULL,1.8,NULL,0),
(156,'http://localhost:9090/files/download/6922130119954_camera1-31.jpg','太太乐鸡精200g',NULL,4,NULL,0),
(157,'http://localhost:9090/files/download/6913102210618_camera1-30.jpg','家乐香菇鸡茸汤料41g',NULL,2.2,NULL,0),
(158,'http://localhost:9090/files/download/6907777820708_camera1-31.jpg','惠宜辣椒粉15g',NULL,7.5,NULL,0),
(159,'http://localhost:9090/files/download/6907777820722_camera1-31.jpg',' 惠宜生姜粉15g',NULL,7.6,NULL,0),
(160,'http://localhost:9090/files/download/6901844710114_camera1-31.jpg','味好美椒盐20g',NULL,2.2,NULL,2),
(161,'http://localhost:9090/files/download/6920181360936_camera1-30.jpg','海星加碘精制盐400g',NULL,3.2,NULL,0),
(162,'http://localhost:9090/files/download/6930096350922_camera0-34.jpg','恒顺料酒500ml',NULL,7,NULL,0),
(163,'http://localhost:9090/files/download/6911567886393_camera0-30.jpg','东古味极鲜酱油150ml',NULL,4.5,NULL,0),
(165,'http://localhost:9090/files/download/6911567881060_camera0-31.jpg','东古一品鲜酱油150ml',NULL,4,NULL,0),
(166,'http://localhost:9090/files/download/6925843403303_camera0-31.jpg','欣和六月鲜酱油160ml',NULL,5.2,NULL,0),
(167,'http://localhost:9090/files/download/6907376820598_camera0-31.jpg','李施德林零度漱口水80ml',NULL,5,NULL,0),
(168,'http://localhost:9090/files/download/6903148232965_camera0-31.jpg','舒肤佳纯白清香沐浴露100ml',NULL,6.6,NULL,0),
(169,'http://localhost:9090/files/download/6924882349016_camera0-31.jpg','美涛定型啫喱水60ml',NULL,6,NULL,0),
(170,'http://localhost:9090/files/download/6902088119435_camera0-31.jpg','清扬男士洗发露活力运动薄荷型50ml',NULL,4.5,NULL,0),
(171,'http://localhost:9090/files/download/6902022138102_camera0-31.jpg','蓝月亮风清白兰洗衣液80g',NULL,6.5,NULL,0),
(172,'http://localhost:9090/files/download/6920354818585_camera1-20.jpg','高露洁亮白小苏打180g',NULL,12.9,NULL,0),
(173,'http://localhost:9090/files/download/6920354808388_camera1-20.jpg','高露洁冰爽180g',NULL,13.9,NULL,3),
(174,'http://localhost:9090/files/download/6921469850194_camera1-20.jpg','舒亮皓齿白80g',NULL,9.9,NULL,0),
(175,'http://localhost:9090/files/download/6901070600128_camera1-21.jpg','云南白药牙膏45g',NULL,9.9,NULL,0),
(176,'http://localhost:9090/files/download/6940477401396_camera1-30.jpg','舒克宝贝儿童牙刷',NULL,6.8,NULL,0),
(177,'http://localhost:9090/files/download/6922266452949_camera1-1.jpg','清风原木纯品金装100x3',NULL,1.8,NULL,3),
(178,'http://localhost:9090/files/download/6914068016115_camera1-20.jpg','洁柔face150x3',NULL,2.53,NULL,0),
(179,'http://localhost:9090/files/download/6953631801604_camera1-21.jpg','斑布100x3',NULL,2.65,NULL,9),
(180,'http://localhost:9090/files/download/6901236378823_camera1-39.jpg','维达婴儿150x3',NULL,6.1,NULL,10),
(181,'http://localhost:9090/files/download/6922868286249_camera1-40.jpg','心相印小黄人150x3',NULL,2.2,NULL,15),
(182,'http://localhost:9090/files/download/6922266457616_camera1-40.jpg','清风原木纯品黑耀系列100x3',NULL,3.8,NULL,0),
(183,'http://localhost:9090/files/download/6918717002160_camera1-39.jpg','洁云绒触感100x3',NULL,1.56,NULL,0),
(184,'http://localhost:9090/files/download/6923589421131_camera1-39.jpg','舒洁至柔升级100x3',NULL,2.9,NULL,3),
(185,'http://localhost:9090/files/download/6903244670166_camera1-40.jpg','心相印红悦100x3',NULL,2.5,NULL,0),
(186,'http://localhost:9090/files/download/6947509910727_camera1-39.jpg','得宝100x3',NULL,4.5,NULL,0),
(187,'http://localhost:9090/files/download/6922266449611_camera1-40.jpg','清风新韧纯品100x3',NULL,1.8,NULL,0),
(188,'http://localhost:9090/files/download/6951481302241_camera1-40.jpg','金鱼100x3',NULL,1.85,NULL,0),
(189,'http://localhost:9090/files/download/6922266444463_camera1-40.jpg','清风原木纯品100x3',NULL,1.6,NULL,0),
(190,'http://localhost:9090/files/download/6914068018171_camera1-40.jpg','洁柔可湿水面纸加厚100x3',NULL,2.7,NULL,4),
(191,'http://localhost:9090/files/download/6901236344033_camera1-23.jpg','维达立体美100x3',NULL,2.5,NULL,3),
(192,'http://localhost:9090/files/download/6914068016535_camera1-31.jpg','洁柔手帕纸',NULL,1,NULL,0),
(193,'http://localhost:9090/files/download/6922868282265_camera1-31.jpg','心相印小黄人手帕纸',NULL,1,NULL,0),
(194,'http://localhost:9090/files/download/6922266457425_camera1-31.jpg','原色纸手帕纸',NULL,1,NULL,0),
(195,'http://localhost:9090/files/download/6922868290932_camera1-31.jpg','心相印茶语手帕纸',NULL,1,NULL,0),
(196,'http://localhost:9090/files/download/6922266426001_camera1-31.jpg','清风质感纯品手帕纸',NULL,1,NULL,0),
(197,'http://localhost:9090/files/download/6901687353417_camera1-30.jpg','迪士尼笔记簿',NULL,3.5,NULL,0),
(198,'http://localhost:9090/files/download/6930114504085_camera0-18.jpg','三角固体棒',NULL,2.5,NULL,2),
(199,'http://localhost:9090/files/download/6951384903194_camera1-40.jpg','蓝色笔袋',NULL,5.5,NULL,0),
(200,'http://localhost:9090/files/download/6933631504811_camera1-31.jpg','晨光拼吧小蜗牛修正带',NULL,3.5,NULL,0),
(201,'http://localhost:9090/files/download/6933093050208_camera0-22.jpg','TAIPAI液体胶',NULL,2.5,NULL,0),
(202,'http://localhost:9090/files/download/6939789303252_camera1-30.jpg','马培德自粘标签',NULL,2.5,NULL,0),
(203,'http://localhost:9090/files/download/6925792550042_camera0-20.jpg','东亚记号笔',NULL,2.6,NULL,0);

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '账号',
  `password` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '电话号码',
  `sex` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '性别',
  `avatar` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '头像',
  `role` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `username` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='用户信息';

/*Data for the table `user` */

insert  into `user`(`id`,`username`,`password`,`name`,`email`,`phone`,`sex`,`avatar`,`role`) values 
(1,'1','1','1',NULL,'19565999949','男','http://localhost:9090/files/download/默认头像.jpg','普通用户'),
(5,'3','3','3',NULL,'123','女','http://localhost:9090/files/download/默认头像.jpg','普通用户'),
(10,'2','2','2',NULL,'18455940682',NULL,'http://localhost:9090/files/download/默认头像.jpg','普通用户');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
