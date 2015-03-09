class BadClass_All {
    public:
BadClass1();
        int getData() const;
    void setData();
    private:
        int data;
    void manipData();
};

class BadClass_Pub_Priv {
    public:
    BadClass_Pub_Priv();
    int getData() const;
    void setData();
    private:
    int data;
    void manipData();
};

class BadClass2 {
public:
    BadClass2() {
            data = 0;
    }
    int getData() const {
    return data;
    }
    void setData() {
data = 0;
    }
private:
    int data;
    void manipData() {
        if (data % 2 != 0) {
            {
                data += 1;
            }
        }
    }

};

class GoodClass {
public:
    GoodClass();
    int getData() const;
    void setData();
private:
    int data;
    void manipData();
};

class GoodClass2 {
public:
    GoodClass2() {
        data = 0;
    }
    int getData() const {

        return data;
    }
    void setData() {
        data = 0;
    }
private:
    int data;
    void manipData() {
        data *= 2;
    }

};