import requests


server_root = 'http://10.248.127.164:8080/'
end_points_dict={"get_emotions":"get_emotions",
                 "get_emotion_intensity":"get_emotion_intensity"}

class EmotionDetector:
    def __init__(self) -> None:
        
        pass

    def get_text_emo(self,text):
        params = {'message': text}
        response = requests.get(server_root+end_points_dict["get_emotions"], params=params)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response data (JSON format)
            ans=response.json()["result"]
            ans=ans.replace(".","")
            if "neutral" in ans:
                return []
            ans=ans.split(",")
            return ans
        else:
            # Print an error message if the request failed
            print(f"Error: {response.status_code}")
            return []
        
    def get_emo_intensity(self,text,emotion):
        params = {'message': text,"emotion":emotion}
        response = requests.get(server_root+end_points_dict["get_emotion_intensity"], params=params)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response data (JSON format)
            return response.json()["result"]
        else:
            # Print an error message if the request failed
            print(f"Error: {response.status_code}")
            return None
    
