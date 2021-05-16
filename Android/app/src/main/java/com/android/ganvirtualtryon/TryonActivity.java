  package com.android.ganvirtualtryon;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.ListAdapter;
import android.widget.Toast;

import com.android.volley.toolbox.ImageLoader;
import com.android.volley.toolbox.NetworkImageView;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;

public class TryonActivity extends AppCompatActivity {
    private NetworkImageView tryon_img;
    private ImageLoader imageLoader;

    private String filePath;

    String filename ="";
    String c_filename ="";
    String h_filename;
    String file_type;

    String selectedItem;
    ImageView GridViewItems,BackSelectedItem;
    private Context mContext;



    DataManager dataManager = DataManager.get_instance();
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tryon);

        tryon_img = findViewById(R.id.tryon_image);
        mContext = this;

        GridView gv_c = (GridView)findViewById(R.id.ImgGridView);
        final ImageAdapter ia_c = new ImageAdapter(this,"clothes","clothes");
        gv_c.setAdapter(ia_c);
        gv_c.setOnItemClickListener(new AdapterView.OnItemClickListener(){
            public void onItemClick(AdapterView<?> parent, View v, int position, long id){

                ia_c.file(position);
                Log.d("click cfile",c_filename);

            }
        });


        GridView gv_h = (GridView)findViewById(R.id.ImgGridView1);
        final ImageAdapter ia_h = new ImageAdapter(this,"human","human");
        gv_h.setAdapter(ia_h);
        gv_h.setOnItemClickListener(new AdapterView.OnItemClickListener(){
            public void onItemClick(AdapterView<?> parent, View v, int position, long id){

                //      ia.callImageViewer(position);
                ia_h.file(position);
                Log.d("click hfile",h_filename);
            }
        });


        findViewById(R.id.btn_try).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                loadImage(c_filename,h_filename);
            }
        });
    }


    public class ImageAdapter extends BaseAdapter {
        private String imgData;
        private String geoData;
        private ArrayList<String> thumbsDataList;
        private ArrayList<String> thumbsIDList;

        private String gallery_path;
        private String image_type;

        ImageView imageView;

        ImageAdapter(Context c, String g_path, String img_type){
            mContext = c;

            this.gallery_path = g_path;
            this.image_type = img_type;

            thumbsDataList = new ArrayList<String>();
            thumbsIDList = new ArrayList<String>();
            getThumbInfo(thumbsIDList, thumbsDataList);
        }

        public void file(int selectedIndex){
            filename = getImageInfo(imgData, geoData, thumbsIDList.get(selectedIndex));
            String [] splited = filename.split("/");
            String b = splited[5];
            String [] a =b.split("\\.");
            Log.d("imgfilename",a[0]);
            if(image_type.equals("clothes")) {
                c_filename = dataManager.find_cfile(a[0]);
                Log.d("real c file",c_filename);
            }
            else if(image_type.equals("human")){
                h_filename =dataManager.find_hfile(a[0]);
                Log.d("real h file",h_filename);
            }

        }


        public boolean deleteSelected(int sIndex){
            return true;
        }

        public int getCount() {
            return thumbsIDList.size();
        }

        public Object getItem(int position) {
            return position;
        }

        public long getItemId(int position) {
            return position;
        }

        public View getView(int position, View convertView, ViewGroup parent) {

            if (convertView == null){
                imageView = new ImageView(mContext);
                imageView.setLayoutParams(new GridView.LayoutParams(105, 105)); // 85 95
                imageView.setAdjustViewBounds(false);
                imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
                imageView.setPadding(20, 20, 20, 20);
             //   imageView.setColorFilter(Color.parseColor("#55ff0000"), PorterDuff.Mode.DST_ATOP);
            }else{
                imageView = (ImageView) convertView;
            }
            BitmapFactory.Options bo = new BitmapFactory.Options();
            bo.inSampleSize = 8;
            Bitmap bmp = BitmapFactory.decodeFile(thumbsDataList.get(position), bo);
            Bitmap resized = Bitmap.createScaledBitmap(bmp, 95, 95, true);
            imageView.setImageBitmap(resized);

            return imageView;
        }

        private void getThumbInfo(ArrayList<String> thumbsIDs, ArrayList<String> thumbsDatas){
            String[] proj = {MediaStore.Images.Media._ID,
                    MediaStore.Images.Media.DATA,
                    MediaStore.Images.Media.DISPLAY_NAME,
                    MediaStore.Images.Media.SIZE};

            Cursor imageCursor = managedQuery(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    proj, MediaStore.Images.Media.DATA + " like ? ", new String[] {"%/" +this.gallery_path + "/%"}, null);


            if (imageCursor != null && imageCursor.moveToFirst()){
                String title;
                String thumbsID;
                String thumbsImageID;
                String thumbsData;
                String data;
                String imgSize;

                int thumbsIDCol = imageCursor.getColumnIndex(MediaStore.Images.Media._ID);
                int thumbsDataCol = imageCursor.getColumnIndex(MediaStore.Images.Media.DATA);
                int thumbsImageIDCol = imageCursor.getColumnIndex(MediaStore.Images.Media.DISPLAY_NAME);
                int thumbsSizeCol = imageCursor.getColumnIndex(MediaStore.Images.Media.SIZE);
                int num = 0;
                do {
                    thumbsID = imageCursor.getString(thumbsIDCol);
                    thumbsData = imageCursor.getString(thumbsDataCol);
                    thumbsImageID = imageCursor.getString(thumbsImageIDCol);
                    imgSize = imageCursor.getString(thumbsSizeCol);
                    num++;
                    if (thumbsImageID != null){
                        thumbsIDs.add(thumbsID);
                        thumbsDatas.add(thumbsData);
                    }
                }while (imageCursor.moveToNext());
            }
            imageCursor.close();
            return;
        }

        private String getImageInfo(String ImageData, String Location, String thumbID){
            String imageDataPath = null;
            String[] proj = {MediaStore.Images.Media._ID,
                    MediaStore.Images.Media.DATA,
                    MediaStore.Images.Media.DISPLAY_NAME,
                    MediaStore.Images.Media.SIZE};

            Cursor imageCursor = managedQuery(MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    proj, "_ID='"+ thumbID +"'", null, null);

            if (imageCursor != null && imageCursor.moveToFirst()){
                if (imageCursor.getCount() > 0){
                    int imgData = imageCursor.getColumnIndex(MediaStore.Images.Media.DATA);
                    imageDataPath = imageCursor.getString(imgData);
                }
            }
            imageCursor.close();
            return imageDataPath;
        }
    }

    private void loadImage(String c, String h){
        String url = "http://3c77d8d7f4ec.ngrok.io/tryon?c="+c+"&h="+h;
        Log.d("url",url);

        imageLoader = CustomVolleyRequest.getInstance(this.getApplicationContext())
                .getImageLoader();
        imageLoader.get(url, ImageLoader.getImageListener(tryon_img,
                R.drawable.ic_launcher_background, android.R.drawable
                        .ic_dialog_alert));
        tryon_img.setImageUrl(url, imageLoader);
    }

    @Override
    public void onStart() {
        super.onStart();
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
    }

    public void onDestroy(){
        super.onDestroy();
    }
}