package com.android.ganvirtualtryon;

import android.util.Log;

import java.io.Serializable;
import java.util.ArrayList;

public class DataManager implements Serializable {
    private ArrayList<Data> c_list = new ArrayList<Data>();
    private ArrayList<Data> h_list = new ArrayList<Data>();
    private static DataManager instance;

    public DataManager(){}

    public int clist_size(){
        return c_list.size();
    }

    public static DataManager get_instance(){
        if(instance == null) instance = new DataManager();
        return instance;
    }

    public void add_clist(Data data){
        c_list.add(data);
    }

    public void add_hlist(Data data){
        h_list.add(data);
    }

    public String find_cfile(String path){
        String c = "";
        Log.d("data_cimagepath",path);
        for(Data c_data : c_list){
            if(c_data.name.equals(path)){
                c = c_data.name;
                Log.d("same_data_c",c);
                Log.d("same_data_c_path",c_data.path);
            }
        }
        Log.d("data_c_suc","c success");
        return c;
    }

    public String find_hfile(String path){
        String h = "";
        for(Data h_data : h_list){
            if(h_data.name.equals(path)){
                h = h_data.name;
                Log.d("same_data_h",h);
                Log.d("same_data_h_path",h_data.path);
            }
        }
        Log.d("data_h_suc","h success");
        return h;
    }
}
