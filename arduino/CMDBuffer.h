// CMDBuffer.h

#ifndef HEADER_CMDBUFFER
  #define HEADER_CMDBUFFER
  
    typedef struct Commands{
  	    byte type;
  	    byte arg1;
  	    byte arg2; 
    } cmd;

class CMDBuffer {
	public:
		CMDBuffer(int size);
		bool isEmpty();
		cmd get_command();
		void put_command();

	private:
		byte byte_buffer[128];
};
#endif
