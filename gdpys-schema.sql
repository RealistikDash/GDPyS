
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
-- Table structure for table `comments`
--

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `level_id` int(11) NOT NULL,
  `content` varchar(256) NOT NULL,
  `timestamp` int(12) NOT NULL,
  `progress` tinyint(3) NOT NULL DEFAULT '0'
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
  `song_id` mediumint(7) UNSIGNED NOT NULL DEFAULT '0',
  `track_id` mediumint(7) UNSIGNED NOT NULL DEFAULT '0',
  `extra_str` varchar(256) NOT NULL,
  `replay` longtext NOT NULL,
  `version` tinyint(3) UNSIGNED NOT NULL DEFAULT '1',
  `game_version` tinyint(2) NOT NULL,
  `binary_version` tinyint(2) NOT NULL,
  `length` tinyint(1) NOT NULL DEFAULT '0',
  `timestamp` int(12) UNSIGNED NOT NULL,
  `update_ts` int(12) NOT NULL,
  `downloads` mediumint(7) UNSIGNED NOT NULL DEFAULT '0',
  `likes` mediumint(7) UNSIGNED NOT NULL DEFAULT '0',
  `stars` tinyint(2) NOT NULL DEFAULT '0',
  `difficulty` tinyint(2) NOT NULL DEFAULT '0',
  `demon_diff` tinyint(2) NOT NULL DEFAULT '0',
  `coins` tinyint(1) NOT NULL,
  `coins_verified` tinyint(1) NOT NULL DEFAULT '0',
  `requested_stars` tinyint(2) NOT NULL,
  `featured_id` int(11) UNSIGNED NOT NULL DEFAULT '0',
  `rate_status` smallint(7) NOT NULL DEFAULT '0',
  `ldm` tinyint(1) NOT NULL,
  `objects` int(11) UNSIGNED NOT NULL,
  `password` varchar(8) NOT NULL,
  `working_time` int(11) UNSIGNED NOT NULL DEFAULT '0',
  `level_ver` tinyint(3) UNSIGNED NOT NULL DEFAULT '0',
  `two_player` tinyint(1) NOT NULL DEFAULT '0',
  `unlisted` tinyint(1) NOT NULL DEFAULT '0',
  `original` int(11) NOT NULL DEFAULT '0'
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
  `download` varchar(128) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(32) NOT NULL,
  `username_safe` varchar(32) NOT NULL,
  `privileges` int(11) UNSIGNED NOT NULL DEFAULT '4',
  `email` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `timestamp` varchar(12) NOT NULL,
  `stars` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `diamonds` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `coins` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `ucoins` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `demons` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `cp` int(6) UNSIGNED NOT NULL DEFAULT '0',
  `colour1` tinyint(4) UNSIGNED NOT NULL DEFAULT '0',
  `colour2` tinyint(4) UNSIGNED NOT NULL DEFAULT '0',
  `icon` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `ship` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `ufo` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `wave` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `ball` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `robot` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `spider` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `explosion` smallint(5) UNSIGNED NOT NULL DEFAULT '0',
  `glow` tinyint(1) UNSIGNED NOT NULL DEFAULT '0',
  `display_icon` tinyint(2) UNSIGNED NOT NULL DEFAULT '0',
  `yt_url` varchar(16) NOT NULL DEFAULT '',
  `twitter_url` varchar(16) NOT NULL DEFAULT '',
  `twitch_url` varchar(16) NOT NULL DEFAULT '',
  `req_status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `user_logins`
--

CREATE TABLE `user_logins` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `ip` varchar(39) NOT NULL,
  `game_ver` tinyint(2) UNSIGNED NOT NULL,
  `bin_ver` tinyint(2) UNSIGNED NOT NULL
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
-- Indexes for table `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `level_id` (`level_id`);

--
-- Indexes for table `levels`
--
ALTER TABLE `levels`
  ADD PRIMARY KEY (`id`),
  ADD KEY `featured_id_2` (`featured_id`);

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
-- Indexes for table `user_logins`
--
ALTER TABLE `user_logins`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `a_comments`
--
ALTER TABLE `a_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `levels`
--
ALTER TABLE `levels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
--
-- AUTO_INCREMENT for table `privileges`
--
ALTER TABLE `privileges`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
--
-- AUTO_INCREMENT for table `songs`
--
ALTER TABLE `songs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=508569;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `user_logins`
--
ALTER TABLE `user_logins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
