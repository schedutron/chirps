--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 10.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: accounts; Type: TABLE; Schema: public; Owner: schedutron
--

CREATE TABLE accounts (
    id bigint
);


ALTER TABLE accounts OWNER TO schedutron;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: schedutron
--

CREATE TABLE admins (
    id integer
);


ALTER TABLE admins OWNER TO schedutron;

--
-- Name: keywords; Type: TABLE; Schema: public; Owner: schedutron
--

CREATE TABLE keywords (
    word character varying
);


ALTER TABLE keywords OWNER TO schedutron;

--
-- Name: messages; Type: TABLE; Schema: public; Owner: schedutron
--

CREATE TABLE messages (
    message character varying
);


ALTER TABLE messages OWNER TO schedutron;

--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: schedutron
--

COPY accounts (id) FROM stdin;
44196397
50393960
1636590253
\.


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: schedutron
--

COPY admins (id) FROM stdin;
257842996
\.


--
-- Data for Name: keywords; Type: TABLE DATA; Schema: public; Owner: schedutron
--

COPY keywords (word) FROM stdin;
feynman
python
pygame
machine learning
apache framework
watson framework
special relativity
general relativity
tensorflow
multithreading
raspberrypi
matplotlib
scala
artificial intelligence
einstein
tkinter
sql
ramanujan
distributed computing
peloton
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: schedutron
--

COPY messages (message) FROM stdin;
Do you employ spaced repetition when you're learning something new?
\.


--
-- Name: public; Type: ACL; Schema: -; Owner: schedutron
--

REVOKE ALL ON SCHEMA public FROM rdsadmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO schedutron;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

