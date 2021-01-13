## 
## Just use docker-compose to spin up this job
##

FROM ubuntu:20.04

RUN apt-get -y -m update && DEBIAN_FRONTEND=noninteractive apt-get install -y cmake g++ git zip wget

RUN mkdir /boost && \
	wget -c https://dl.bintray.com/boostorg/release/1.75.0/source/boost_1_75_0.tar.gz -O - | tar -xz -C /boost && \
	cd /boost/boost_1_75_0/ && \
	./bootstrap.sh && \
	./b2 tools/bcp && \
	mkdir /mp && \
	bin.v2/tools/bcp/gcc-9/release/link-static/bcp multiprecision/cpp_bin_float.hpp /mp && \
	zip -r /boost_mp.zip /mp && \
	tar czf /boost_mp.tar.gz /mp
	
CMD cp /*.tar.gz /output