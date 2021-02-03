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
	mkdir /boost_multiprecision && \
	bin.v2/tools/bcp/gcc-9/release/link-static/bcp multiprecision/cpp_bin_float.hpp multiprecision/eigen.hpp /boost_multiprecision && \
	zip -r /boost_multiprecision.zip /boost_multiprecision && \
	tar czf /boost_multiprecision.tar.gz /boost_multiprecision
	
CMD cp /*.tar.gz /output