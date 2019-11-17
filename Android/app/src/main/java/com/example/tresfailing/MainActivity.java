package com.example.tresfailing;

import androidx.appcompat.app.AppCompatActivity;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Debug;
import android.os.Handler;
import android.os.Looper;
import android.text.format.Formatter;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;;

import android.app.Activity;
import android.widget.Toast;

import com.illposed.osc.*;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Date;
import java.util.List;

public class MainActivity extends AppCompatActivity{
    private static final String TAG = MainActivity.class.getName();

    boolean isOSCRunning = false;

    private float proximity = 1f;
    private float sound_duration;

    private String myIP = "192.168.43.37";
    private int myPort = 5005;

    // OSC In/Out
    private OSCPortOut sender;
    public OSCPortIn receiver;
    public static List<Object> messageIn;

    Button buttonConnect;
    TextView proximityView, durationView;

    // This thread will contain all the code that pertains to OSC
    private Thread oscThread = new Thread() {
        @Override
        public void run() {
            /* The first part of the run() method initializes the OSCPortOut for sending messages.
             *
             * For more advanced apps, where you want to change the address during runtime, you will want
             * to have this section in a different thread, but since we won't be changing addresses here,
             * we only have to initialize the address once.
             */

            try {
                // Connect to some IP address and port
                sender = new OSCPortOut(InetAddress.getByName(myIP), myPort);
            } catch(UnknownHostException e) {
                // Error handling when your IP isn't found
                Log.e("OSC Error", String.valueOf(e));
                e.printStackTrace();
                return;
            } catch(Exception e) {
                // Error handling for any other errors
                Log.e("OSC Error", String.valueOf(e));
                e.printStackTrace();
                return;
            }

            try{
                showToast("Connecting...");
                // Open PortIn for entering communication
                receiver = new OSCPortIn(myPort);
                OSCListener listener = new OSCListener() {
                    @Override // Deal with messages received
                    public void acceptMessage(Date date, OSCMessage oscMessage) {
                        messageIn = oscMessage.getArguments();
                        //showToast(messageIn.get(0).toString());
                        //Log.d(TAG, messageIn.toString());

                        proximity = (float) messageIn.get(0);
                    }
                };

                // Start listening to port
                try {
                    showToast("Listening...");
                    receiver.addListener("/phone", listener);
                    receiver.startListening();
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Error: " + e, Toast.LENGTH_SHORT).show();
                }

            } catch (Exception e){
                showToast("Failed to connect");
                e.printStackTrace();
            }

        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        oscThread.start();

        // Create UI
        buttonConnect = (Button) findViewById(R.id.connect);
        proximityView = (TextView) findViewById(R.id.proximityText);
        durationView = (TextView) findViewById(R.id.durationText);

        initUI.start();

        proximityThread.start();

        buttonConnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                playSound(1500, 44100*2);
            }
        });

    }

    /*buttonConnect.setOnClickListener(new View.OnClickListener() {
        public void onClick(View v) {
            // Code here executes on main thread after user presses button
            // Runs OSC. If already running, returns an error without interrupting the thread
            try{
                if(!isOSCRunning){
                    oscThread.start();
                }
                else if (!receiver.isListening()) {
                    oscThread.start();
                }
                else{
                    showToast("OSC thread already running...");
                }
            }catch (Exception e){
                Log.e("OSC Error", String.valueOf(e));
                showToast(e.toString());
            }
        }
    });*/

    // Connect to client
    /*buttonConnect.setOnClickListener(new View.OnClickListener(){
        @Override
        public void onClick (View view) {

            // Runs OSC. If already running, returns an error without interrupting the thread
            try{
                if(!isOSCRunning){
                    oscThread.start();
                }
                else if (!receiver.isListening()) {
                    oscThread.start();
                }
                else{
                    showToast("OSC thread already running...");
                }
            }catch (Exception e){
                showToast(e.toString());
            }

    //        // Init UI. Returns error if already running
    //        try{
    //            initUi.start();
    //        } catch (Exception e){
    //            showToast(e.toString());
    //        }
        }
    }*/

    // Proximity check Thread
    final Thread proximityThread = new Thread(){
        public void run(){
            try{
                while(true){
                    if (proximity < 1){
                        showToast("Trespassing!");
                        sound_duration = 1000 * proximity;
                        playSound(1500, 44100);
                        Thread.sleep((long)sound_duration);
                    }
                }
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    };

    // UI Thread
    final Thread initUI = new Thread(){
        @Override
        public void run(){
            try{
                while(true){
                    Thread.sleep(1); // Refresh every 1ms
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            try{
                                proximityView.setText("Proximity: " + String.format("%.5f", proximity));
                                durationView.setText("Duration: " + String.format("%.5f", sound_duration));
                            } catch (Exception e){
                                e.printStackTrace();
                            }
                        }
                    });
                }
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    };

    private void playSound(double frequency, int duration) {
        // AudioTrack definition
        int mBufferSize = AudioTrack.getMinBufferSize(44100,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_8BIT);

        AudioTrack mAudioTrack = new AudioTrack(AudioManager.STREAM_MUSIC, 44100,
                AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT,
                mBufferSize, AudioTrack.MODE_STREAM);

        // Sine wave
        double[] mSound = new double[4410];
        short[] mBuffer = new short[duration];
        for (int i = 0; i < mSound.length; i++) {
            mSound[i] = Math.sin((2.0*Math.PI * i/(44100/frequency)));
            mBuffer[i] = (short) (mSound[i]*Short.MAX_VALUE);
        }

        mAudioTrack.setStereoVolume(AudioTrack.getMaxVolume(), AudioTrack.getMaxVolume());
        mAudioTrack.play();

        mAudioTrack.write(mBuffer, 0, mSound.length);
        mAudioTrack.stop();
        mAudioTrack.release();

    }

    public void showToast(final String msg) {
        runOnUiThread(new Runnable() {
            public void run() {
                Toast.makeText(MainActivity.this, msg, Toast.LENGTH_SHORT).show();
            }
        });
    }

}
