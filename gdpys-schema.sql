-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Feb 21, 2021 at 10:57 PM
-- Server version: 5.7.28-0ubuntu0.18.04.4
-- PHP Version: 7.1.33-9+ubuntu18.04.1+deb.sury.org+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `gdpys`
--

-- --------------------------------------------------------

--
-- Table structure for table `a_comments`
--

CREATE TABLE `a_comments` (
  `id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `likes` int(6) NOT NULL DEFAULT '0',
  `content` varchar(256) NOT NULL,
  `timestamp` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `levels`
--

CREATE TABLE `levels` (
  `id` int(11) NOT NULL,
  `name` varchar(32) NOT NULL,
  `user_id` int(11) NOT NULL,
  `description` varchar(256) NOT NULL,
  `song_id` mediumint(7) NOT NULL,
  `extra_str` varchar(256) NOT NULL,
  `replay` longtext NOT NULL,
  `game_version` tinyint(2) NOT NULL,
  `binary_version` tinyint(2) NOT NULL,
  `timestamp` int(12) NOT NULL,
  `downloads` mediumint(7) NOT NULL DEFAULT '0',
  `likes` mediumint(7) NOT NULL DEFAULT '0',
  `stars` tinyint(2) NOT NULL DEFAULT '0',
  `difficulty` tinyint(2) NOT NULL DEFAULT '0',
  `demon_diff` tinyint(2) NOT NULL DEFAULT '0',
  `coins` tinyint(1) NOT NULL,
  `coins_verified` tinyint(1) NOT NULL DEFAULT '0',
  `requested_stars` tinyint(2) NOT NULL,
  `featured_id` int(11) NOT NULL DEFAULT '0',
  `epic` tinyint(1) NOT NULL DEFAULT '0',
  `ldm` tinyint(1) NOT NULL,
  `objects` int(11) NOT NULL,
  `password` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `privileges`
--

CREATE TABLE `privileges` (
  `id` int(11) NOT NULL,
  `name` varchar(16) NOT NULL,
  `description` varchar(128) NOT NULL,
  `privilege` int(12) NOT NULL,
  `rgb` varchar(11) NOT NULL DEFAULT '255,255,255'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `songs`
--

CREATE TABLE `songs` (
  `id` int(11) NOT NULL,
  `title` varchar(32) NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_name` varchar(32) NOT NULL,
  `size` float NOT NULL DEFAULT '0',
  `author_yt` varchar(32) NOT NULL DEFAULT '',
  `download` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(32) NOT NULL,
  `username_safe` varchar(32) NOT NULL,
  `privileges` int(11) NOT NULL DEFAULT '4',
  `email` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `timestamp` varchar(12) NOT NULL,
  `stars` int(6) NOT NULL DEFAULT '0',
  `diamonds` int(6) NOT NULL DEFAULT '0',
  `coins` int(6) NOT NULL DEFAULT '0',
  `ucoins` int(6) NOT NULL DEFAULT '0',
  `demons` int(6) NOT NULL DEFAULT '0',
  `cp` int(6) NOT NULL DEFAULT '0',
  `colour1` tinyint(4) NOT NULL DEFAULT '0',
  `colour2` tinyint(4) NOT NULL DEFAULT '0',
  `icon` smallint(5) NOT NULL DEFAULT '0',
  `ship` smallint(5) NOT NULL DEFAULT '0',
  `ufo` smallint(5) NOT NULL DEFAULT '0',
  `wave` smallint(5) NOT NULL DEFAULT '0',
  `ball` smallint(5) NOT NULL DEFAULT '0',
  `robot` smallint(5) NOT NULL DEFAULT '0',
  `spider` smallint(5) NOT NULL DEFAULT '0',
  `explosion` smallint(5) NOT NULL DEFAULT '0',
  `glow` tinyint(1) NOT NULL DEFAULT '0',
  `display_icon` tinyint(2) NOT NULL DEFAULT '0',
  `yt_url` varchar(16) NOT NULL DEFAULT '',
  `twitter_url` varchar(16) NOT NULL DEFAULT '',
  `twitch_url` varchar(16) NOT NULL DEFAULT '',
  `req_status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `a_comments`
--
ALTER TABLE `a_comments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `levels`
--
ALTER TABLE `levels`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `privileges`
--
ALTER TABLE `privileges`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `songs`
--
ALTER TABLE `songs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `a_comments`
--
ALTER TABLE `a_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
--
-- AUTO_INCREMENT for table `levels`
--
ALTER TABLE `levels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `privileges`
--
ALTER TABLE `privileges`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT for table `songs`
--
ALTER TABLE `songs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=123124;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
