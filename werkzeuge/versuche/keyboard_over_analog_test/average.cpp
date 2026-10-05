class Average
{ 
      int buffsize;    //Mittelwert ueber x Messwerte
      float average_buff[31];
      int p; //zeigt auf das Element in das der naechste Wert eingetragen wird
      int full; //zeigt an, wie voll das Array schon ist.
      float r; //Rueckgabewert
      float sum; //Zwischenergebnis
  
  public: void init()     
  {        
     buffsize=30;
     p=0;   //Pointer zeigt auf das erste Element in average_buff
     full=0;//Das Array ist noch nicht voll beschrieben.
     r=0;
     sum=0;
  } 
  
  public: float glaetten(float v)
  {
      int i;
      if(p>=buffsize) {full=1; p=0;}
      average_buff[p]=v;
      p++;
      sum=0;  
      for(i=0;i<buffsize;i++)
      {
        sum=sum+average_buff[i];
      }  
      if(full==1){r=sum/buffsize;} else {r=sum/p;}
      return r;  
  
  }
  
  public: float glaetten_winkel(float v)
  {
    int i;
    //Testen, ob der Winkel < 180 Grad zu einem
    //der Eintraege in average_buff ist
    if(full==1 || p>0)
    {
      if(r-v>180) {v=v+360;}
      if(r-v<-180){v=v-360;}
    }
    if(p>=buffsize) {full=1; p=0;}
    average_buff[p]=v;
    p++;
    sum=0;  
    for(i=0;i<buffsize;i++)
    {
      sum=sum+average_buff[i];
    }  
    if(full==1){r=sum/buffsize;} else {r=sum/p;}
    if(r>=360){return r-360;}else{return r;} 
  }

  public: float p_buff()
  {
    return *average_buff;
  }

  public: int get_p()
  {
    return p;
  }

  public: float get_buff_value(int p)
  {
    return average_buff[p];
  }
};
