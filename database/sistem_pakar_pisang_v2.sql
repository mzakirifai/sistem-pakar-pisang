-- Basis pengetahuan v2: Sistem Pakar Diagnosis Kematangan Pisang Pascapanen
-- Perubahan dari v1:
--   * attributes.jenis  : membedakan atribut input dan atribut antara (dugaan_awal)
--   * rules.sumber      : rujukan jurnal per rule; 'CF: asumsi tim' = nilai CF bukan dari jurnal
--   * warna_kulit       : nilai 'Kuning berbintik coklat' dihapus (bercak sudah punya atribut sendiri)
--   * dugaan_awal       : Mentah, Mengkal, Matang (fase warna); kelas akhir ada di rules.kesimpulan
--   * rule layer 2      : M1-M3, K1-K3, O1-O6, T1-T3; CF = 1,0 - 0,2 x tingkat penyimpangan dari profil khas
--
-- PERINGATAN: skrip ini MENGHAPUS dan membuat ulang keempat tabel (DROP TABLE).
-- Impor ke database uji (mis. sistem_pakar_pisang_v2) dulu, bukan ke database cloud.

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `rule_conditions`;
DROP TABLE IF EXISTS `rules`;
DROP TABLE IF EXISTS `attribute_values`;
DROP TABLE IF EXISTS `attributes`;

START TRANSACTION;

CREATE TABLE `attributes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_atribut` varchar(50) NOT NULL,
  `jenis` varchar(10) NOT NULL DEFAULT 'input',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nama_atribut` (`nama_atribut`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `attribute_values` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attribute_id` int(11) NOT NULL,
  `nilai` varchar(50) NOT NULL,
  `urutan` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attribute_id` (`attribute_id`),
  CONSTRAINT `attribute_values_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `attributes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_rule` varchar(10) NOT NULL,
  `kesimpulan` varchar(50) NOT NULL,
  `rekomendasi` text NOT NULL,
  `nilai_cf` float NOT NULL,
  `layer` int(11) NOT NULL DEFAULT 2,
  `sumber` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rule` (`kode_rule`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `rule_conditions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_id` int(11) NOT NULL,
  `attribute_value_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rule_id` (`rule_id`),
  KEY `attribute_value_id` (`attribute_value_id`),
  CONSTRAINT `rule_conditions_ibfk_1` FOREIGN KEY (`rule_id`) REFERENCES `rules` (`id`),
  CONSTRAINT `rule_conditions_ibfk_2` FOREIGN KEY (`attribute_value_id`) REFERENCES `attribute_values` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `attributes` (`id`, `nama_atribut`, `jenis`) VALUES
(1, 'warna_kulit', 'input'),
(2, 'tekstur', 'input'),
(3, 'aroma', 'input'),
(4, 'bercak_kulit', 'input'),
(5, 'dugaan_awal', 'antara');

INSERT INTO `attribute_values` (`id`, `attribute_id`, `nilai`, `urutan`) VALUES
(1, 1, 'Hijau penuh', 1),
(2, 1, 'Hijau kekuningan', 2),
(3, 1, 'Kuning penuh', 3),
(4, 2, 'Keras', 1),
(5, 2, 'Agak lunak', 2),
(6, 2, 'Lunak', 3),
(7, 3, 'Tidak beraroma', 1),
(8, 3, 'Beraroma ringan', 2),
(9, 3, 'Beraroma kuat', 3),
(10, 4, 'Tidak ada', 1),
(11, 4, 'Sedikit', 2),
(12, 4, 'Banyak', 3),
(13, 5, 'Mentah', 1),
(14, 5, 'Mengkal', 2),
(15, 5, 'Matang', 3);

INSERT INTO `rules` (`id`, `kode_rule`, `kesimpulan`, `rekomendasi`, `nilai_cf`, `layer`, `sumber`) VALUES
(1, 'L1', 'Mentah', 'Dugaan awal dari warna kulit, masih perlu dikonfirmasi ciri lain', 0.8, 1, 'Sutowijoyo & Widodo (2013); Sularida dkk. (2018); Zhu dkk. (2018); Maduwanthi & Marapana (2017, 2019); CF: asumsi tim'),
(2, 'L2', 'Mengkal', 'Dugaan awal dari warna kulit, masih perlu dikonfirmasi ciri lain', 0.6, 1, 'Sutowijoyo & Widodo (2013); Sularida dkk. (2018); Zhu dkk. (2018); Maduwanthi & Marapana (2017, 2019); CF: asumsi tim'),
(3, 'L3', 'Matang', 'Dugaan awal dari warna kulit, masih perlu dikonfirmasi ciri lain', 0.8, 1, 'Sutowijoyo & Widodo (2013); Sularida dkk. (2018); Zhu dkk. (2018); Maduwanthi & Marapana (2017, 2019); CF: asumsi tim'),
(4, 'M1', 'Mentah', 'Simpan dulu, belum layak dikonsumsi langsung', 1.0, 2, 'Zhu dkk. (2018): kekerasan dan aroma fase hijau; CF: asumsi tim'),
(5, 'M2', 'Mentah', 'Simpan dulu, belum layak dikonsumsi langsung', 0.8, 2, 'Zhu dkk. (2018): kekerasan dan aroma fase hijau; CF: asumsi tim'),
(6, 'M3', 'Mentah', 'Simpan dulu, belum layak dikonsumsi langsung', 0.8, 2, 'Zhu dkk. (2018): kekerasan dan aroma fase hijau; CF: asumsi tim'),
(7, 'K1', 'Mengkal', 'Tunggu 1-2 hari lagi (perkiraan, bergantung varietas dan suhu simpan)', 1.0, 2, 'Zhu dkk. (2018): fase menguning; Sutowijoyo & Widodo (2013), Tabel 1-2: waktu antar-skala; CF: asumsi tim'),
(8, 'K2', 'Mengkal', 'Tunggu 1-2 hari lagi (perkiraan, bergantung varietas dan suhu simpan)', 0.8, 2, 'Zhu dkk. (2018): fase menguning; Sutowijoyo & Widodo (2013), Tabel 1-2: waktu antar-skala; CF: asumsi tim'),
(9, 'K3', 'Mengkal', 'Tunggu 1-2 hari lagi (perkiraan, bergantung varietas dan suhu simpan)', 0.8, 2, 'Zhu dkk. (2018): fase menguning; Sutowijoyo & Widodo (2013), Tabel 1-2: waktu antar-skala; CF: asumsi tim'),
(10, 'O1', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 1.0, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(11, 'O2', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 1.0, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(12, 'O3', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 0.8, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(13, 'O4', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 0.8, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(14, 'O5', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 0.8, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(15, 'O6', 'Matang Optimal', 'Layak konsumsi langsung/dijual', 0.8, 2, 'Zhu dkk. (2018): matang penuh; Sutowijoyo & Widodo (2013): skala 5 layak konsumsi; Kosasih (2021): bintik sedikit; CF: asumsi tim'),
(16, 'T1', 'Terlalu Matang', 'Sudah lewat masak, tetapi masih layak dikonsumsi; segera konsumsi atau olah', 1.0, 2, 'Dayan dkk. (2026): bercak cokelat; Sutowijoyo & Widodo (2013): skala 6-7 lewat masak; CF: asumsi tim'),
(17, 'T2', 'Terlalu Matang', 'Sudah lewat masak, tetapi masih layak dikonsumsi; segera konsumsi atau olah', 0.8, 2, 'Dayan dkk. (2026): bercak cokelat; Sutowijoyo & Widodo (2013): skala 6-7 lewat masak; CF: asumsi tim'),
(18, 'T3', 'Terlalu Matang', 'Sudah lewat masak, tetapi masih layak dikonsumsi; segera konsumsi atau olah', 0.8, 2, 'Dayan dkk. (2026): bercak cokelat; Sutowijoyo & Widodo (2013): skala 6-7 lewat masak; CF: asumsi tim');

INSERT INTO `rule_conditions` (`id`, `rule_id`, `attribute_value_id`) VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3),
(4, 4, 13),
(5, 4, 4),
(6, 4, 7),
(7, 4, 10),
(8, 5, 13),
(9, 5, 5),
(10, 5, 7),
(11, 5, 10),
(12, 6, 13),
(13, 6, 4),
(14, 6, 8),
(15, 6, 10),
(16, 7, 14),
(17, 7, 5),
(18, 7, 8),
(19, 7, 10),
(20, 8, 14),
(21, 8, 4),
(22, 8, 8),
(23, 8, 10),
(24, 9, 14),
(25, 9, 5),
(26, 9, 7),
(27, 9, 10),
(28, 10, 15),
(29, 10, 6),
(30, 10, 9),
(31, 10, 10),
(32, 11, 15),
(33, 11, 6),
(34, 11, 9),
(35, 11, 11),
(36, 12, 15),
(37, 12, 5),
(38, 12, 9),
(39, 12, 10),
(40, 13, 15),
(41, 13, 5),
(42, 13, 9),
(43, 13, 11),
(44, 14, 15),
(45, 14, 6),
(46, 14, 8),
(47, 14, 10),
(48, 15, 15),
(49, 15, 6),
(50, 15, 8),
(51, 15, 11),
(52, 16, 15),
(53, 16, 6),
(54, 16, 9),
(55, 16, 12),
(56, 17, 15),
(57, 17, 5),
(58, 17, 9),
(59, 17, 12),
(60, 18, 15),
(61, 18, 6),
(62, 18, 8),
(63, 18, 12);

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
