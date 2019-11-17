using UnityEngine;
using System.Collections;

public class ReceivePosition : MonoBehaviour {
    
   	public OSC osc;

    // Indexes:
    int headID = 9;
    int handLID = 15;
    int handRID = 10;
    int pelvID = 6;
    int ankleLID = 5;
    int ankleRID = 0;

    // GameObjcts:
    GameObject headObj;
    GameObject handLObj;
    GameObject handRObj;
    GameObject pelvObj;
    GameObject ankleLObj;
    GameObject ankleRObj;


    // Use this for initialization
    void Start () {

        headObj = GameObject.Find("Head");
        handLObj = GameObject.Find("HandL");
        handRObj = GameObject.Find("HandR");
        pelvObj = GameObject.Find("Pelv");
        ankleLObj = GameObject.Find("AnkleL");
        ankleRObj = GameObject.Find("AnkleR");
        osc.SetAddressHandler("/cam0/0" , OnReceiveCam0 );
        osc.SetAddressHandler("/cam1/0", OnReceiveCam1);
        //osc.SetAddressHandler("/CubeY", OnReceiveY);
        //osc.SetAddressHandler("/CubeZ", OnReceiveZ);
    }
	
	// Update is called once per frame
	void Update () {
        //headObj.transform.localPosition = new Vector3(2f, 3f, 4f);
    }

    // Assume cam0 gives X axis
	void OnReceiveCam0(OscMessage message){
        headObj.transform.localPosition     = new Vector3(message.GetFloat(headID),    -message.GetFloat(headID + 1),   headObj.transform.localPosition.z);
        handLObj.transform.localPosition    = new Vector3(message.GetFloat(handLID),   -message.GetFloat(handLID + 1),  handLObj.transform.localPosition.z);
        handRObj.transform.localPosition    = new Vector3(message.GetFloat(handRID),   -message.GetFloat(handRID + 1),  handRObj.transform.localPosition.z);
        pelvObj.transform.localPosition     = new Vector3(message.GetFloat(pelvID),    -message.GetFloat(pelvID + 1),   pelvObj.transform.localPosition.z);
        ankleLObj.transform.localPosition   = new Vector3(message.GetFloat(ankleLID),  -message.GetFloat(ankleLID + 1), ankleLObj.transform.localPosition.z);
        ankleRObj.transform.localPosition   = new Vector3(message.GetFloat(ankleRID),  -message.GetFloat(ankleRID + 1), ankleRObj.transform.localPosition.z);
	}

    // Assume cam1 gives Y axis
    void OnReceiveCam1(OscMessage message) {
        headObj.transform.localPosition     = new Vector3(headObj.transform.localPosition.x,  headObj.transform.localPosition.y, message.GetFloat(headID));
        handLObj.transform.localPosition    = new Vector3(handLObj.transform.localPosition.x, handLObj.transform.localPosition.y, message.GetFloat(handLID));
        handRObj.transform.localPosition    = new Vector3(handRObj.transform.localPosition.x, handRObj.transform.localPosition.y, message.GetFloat(handRID));
        pelvObj.transform.localPosition     = new Vector3(pelvObj.transform.localPosition.x,  pelvObj.transform.localPosition.y, message.GetFloat(pelvID));
        ankleLObj.transform.localPosition   = new Vector3(ankleLObj.transform.localPosition.x, ankleLObj.transform.localPosition.y, message.GetFloat(ankleLID));
        ankleRObj.transform.localPosition   = new Vector3(ankleRObj.transform.localPosition.x, ankleRObj.transform.localPosition.y, message.GetFloat(ankleRID));
    }

    void OnReceiveY(OscMessage message) {
        float y = message.GetFloat(0);

        Vector3 position = transform.position;

        position.y = y;

        transform.position = position;
    }

    void OnReceiveZ(OscMessage message) {
        float z = message.GetFloat(0);

        Vector3 position = transform.position;

        position.z = z;

        transform.position = position;
    }


}
